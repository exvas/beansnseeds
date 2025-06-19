import frappe
from frappe.utils import flt
from datetime import datetime

def execute(filters=None):
    if not filters:
        filters = {}

    # Convert string to date
    if filters.get("from_date"):
        filters["from_date"] = datetime.strptime(filters["from_date"], "%Y-%m-%d").date()
    if filters.get("to_date"):
        filters["to_date"] = datetime.strptime(filters["to_date"], "%Y-%m-%d").date()

    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    customer = filters.get("customer")
    salesperson = filters.get("sales_person")

    # Fetch Sales Invoices
    invoices = frappe.db.sql("""
        SELECT
            si.name AS invoice,
            si.customer,
            si.posting_date AS invoice_date,
            si.base_grand_total AS grand_total,
            st.sales_person AS sales_person
        FROM `tabSales Invoice` si
        LEFT JOIN (
            SELECT parent, sales_person
            FROM `tabSales Team`
            GROUP BY parent
        ) st ON st.parent = si.name
        WHERE si.docstatus = 1
        {customer_condition}
        {sales_person_condition}
    """.format(
        customer_condition="AND si.customer = %(customer)s" if customer else "",
        sales_person_condition="AND st.sales_person = %(sales_person)s" if salesperson else ""
    ), filters, as_dict=1)

    invoice_totals = {inv.invoice: inv.grand_total for inv in invoices}
    invoice_customers = {inv.invoice: inv.customer for inv in invoices}
    invoice_salespersons = {inv.invoice: inv.sales_person for inv in invoices}

    # Get PREVIOUS payments (before from_date)
    prev_payments_pe = frappe.db.sql("""
        SELECT
            pei.reference_name AS invoice,
            SUM(pei.allocated_amount) AS allocated_amount
        FROM `tabPayment Entry` pe
        INNER JOIN `tabPayment Entry Reference` pei ON pe.name = pei.parent
        WHERE pe.docstatus = 1
        AND pei.reference_doctype = 'Sales Invoice'
        AND pe.posting_date < %(from_date)s
        GROUP BY pei.reference_name
    """, filters, as_dict=1)

    prev_payments_je = frappe.db.sql("""
        SELECT
            jea.reference_name AS invoice,
            SUM(jea.credit_in_account_currency) AS allocated_amount
        FROM `tabJournal Entry` je
        INNER JOIN `tabJournal Entry Account` jea ON je.name = jea.parent
        WHERE je.docstatus = 1
        AND jea.reference_type = 'Sales Invoice'
        AND jea.reference_name IS NOT NULL
        AND je.posting_date < %(from_date)s
        GROUP BY jea.reference_name
    """, filters, as_dict=1)

    previous_paid_map = {}
    for row in prev_payments_pe + prev_payments_je:
        previous_paid_map[row.invoice] = previous_paid_map.get(row.invoice, 0) + flt(row.allocated_amount)

    # Get CURRENT payments (between from_date and to_date)
    payments = frappe.db.sql("""
        SELECT
            pe.name AS pe_reference,
            pe.posting_date AS payment_date,
            pei.reference_name AS invoice,
            pei.allocated_amount AS allocated_amount
        FROM `tabPayment Entry` pe
        INNER JOIN `tabPayment Entry Reference` pei ON pei.parent = pe.name
        WHERE pe.docstatus = 1
        AND pei.reference_doctype = 'Sales Invoice'
        AND pe.posting_date BETWEEN %(from_date)s AND %(to_date)s
    """, filters, as_dict=1)

    journals = frappe.db.sql("""
        SELECT
            je.name AS pe_reference,
            je.posting_date AS payment_date,
            jea.reference_name AS invoice,
            jea.credit_in_account_currency AS allocated_amount
        FROM `tabJournal Entry` je
        INNER JOIN `tabJournal Entry Account` jea ON je.name = jea.parent
        WHERE je.docstatus = 1
        AND jea.reference_type = 'Sales Invoice'
        AND jea.reference_name IS NOT NULL
        AND je.posting_date BETWEEN %(from_date)s AND %(to_date)s
    """, filters, as_dict=1)

    all_payments = payments + journals

    # Group payments by date
    payments_by_date = {}
    for pay in all_payments:
        date = pay.payment_date
        invoice = pay.invoice
        amt = flt(pay.allocated_amount)
        ref = pay.pe_reference

        if date not in payments_by_date:
            payments_by_date[date] = []
        payments_by_date[date].append({
            "invoice": invoice,
            "allocated_amount": amt,
            "pe_reference": ref
        })

    sorted_dates = sorted(payments_by_date.keys())
    paid_cumulative = {}  # Tracks daily paid + previous paid
    data = []

    for date in sorted_dates:
        daily_payments = payments_by_date[date]

        for pay in daily_payments:
            invoice = pay["invoice"]
            allocated_amt = flt(pay["allocated_amount"])
            pe_reference = pay["pe_reference"]

            previous_paid = previous_paid_map.get(invoice, 0)
            paid_before_today = paid_cumulative.get(invoice, 0)
            total_paid_till_now = previous_paid + paid_before_today + allocated_amt
            grand_total = invoice_totals.get(invoice, 0)

            data.append({
                "date": date,
                "customer": invoice_customers.get(invoice),
                "sales_person": invoice_salespersons.get(invoice),
                "si_reference": invoice,
                "pe_reference": pe_reference,
                "grand_total": grand_total,
                "previous_allocated_amount": previous_paid,
                "allocated_amount": allocated_amt,
                "outstanding_amount": max(grand_total - total_paid_till_now, 0)
            })

            paid_cumulative[invoice] = paid_before_today + allocated_amt

    total_grand = sum(d["grand_total"] for d in data)
    total_paid = sum(d["allocated_amount"] for d in data)
    total_outstanding = sum(d["outstanding_amount"] for d in data)

    chart = {
        "data": {
            "labels": [d["date"].strftime('%d-%m-%Y') for d in data],
            "datasets": [
                {"name": "Total Invoiced", "values": [d["grand_total"] for d in data]},
                {"name": "Allocated Amount", "values": [d["allocated_amount"] for d in data]},
                {"name": "Outstanding", "values": [d["outstanding_amount"] for d in data]},
            ]
        },
        "type": "bar",
        "colors": ["#5e64ff", "#28a745", "#ff4d4d"]
    }

    return get_columns(), data, None, chart, get_report_summary(total_grand, total_paid, total_outstanding)

def get_columns():
    return [
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 110},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Data", "width": 200},
        {"label": "Sales Person", "fieldname": "sales_person", "fieldtype": "Data", "width": 150},
        {"label": "SI Reference", "fieldname": "si_reference", "fieldtype": "Link", "options": "Sales Invoice", "width": 200},
        {"label": "PE/JE Reference", "fieldname": "pe_reference", "fieldtype": "Data", "width": 200},
        {"label": "Grand Total", "fieldname": "grand_total", "fieldtype": "Currency", "width": 120},
        {"label": "Previous Allocated", "fieldname": "previous_allocated_amount", "fieldtype": "Currency", "width": 180},
        {"label": "Allocated Amount", "fieldname": "allocated_amount", "fieldtype": "Currency", "width": 180},
        {"label": "Outstanding Amount", "fieldname": "outstanding_amount", "fieldtype": "Currency", "width": 180, "add_total_row": True},
    ]

def get_report_summary(grand_total, paid_total, outstanding_total):
    return [
        {"label": "Total Invoiced", "value": grand_total, "indicator": "Blue"},
        {"label": "Total Allocated", "value": paid_total, "indicator": "Green"},
        {"label": "Outstanding", "value": outstanding_total, "indicator": "Red"},
    ]
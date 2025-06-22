import frappe
from frappe.utils import flt, cstr
from datetime import datetime

def execute(filters=None):
    if not filters:
        filters = {}

    # Convert string to date
    if filters.get("from_date"):
        if isinstance(filters["from_date"], str):
            filters["from_date"] = datetime.strptime(filters["from_date"], "%Y-%m-%d").date()
    if filters.get("to_date"):
        if isinstance(filters["to_date"], str):
            filters["to_date"] = datetime.strptime(filters["to_date"], "%Y-%m-%d").date()

    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    customer = filters.get("customer")
    salesperson = filters.get("sales_person")
    
    # Get currency precision from system settings
    precision = int(frappe.db.get_single_value("System Settings", "currency_precision") or 3)

    # Build dynamic conditions
    conditions = []
    if customer:
        conditions.append("AND si.customer = %(customer)s")
    if salesperson:
        conditions.append("AND st.sales_person = %(sales_person)s")
    
    # Add date filter for payments in the specified range
    if from_date and to_date:
        conditions.append("AND si.posting_date <= %(to_date)s")

    conditions_str = " ".join(conditions)

    # Fetch Sales Invoices with customer names and sales person using INNER JOIN
    invoices = frappe.db.sql("""
        SELECT DISTINCT
            si.name AS invoice,
            si.customer,
            COALESCE(c.customer_name, si.customer) AS customer_name,
            si.posting_date AS invoice_date,
            si.base_grand_total AS grand_total,
            st.sales_person
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Team` st ON st.parent = si.name
        LEFT JOIN `tabCustomer` c ON c.name = si.customer
        WHERE si.docstatus = 1
        AND st.sales_person IS NOT NULL
        AND st.sales_person != ''
        {conditions}
        ORDER BY si.posting_date DESC
    """.format(conditions=conditions_str), filters, as_dict=1)

    # Filter and validate invoices
    valid_invoices = []
    for inv in invoices:
        if inv.sales_person and inv.sales_person.strip():
            if not salesperson or inv.sales_person == salesperson:
                valid_invoices.append(inv)

    if not valid_invoices:
        return get_columns(), [], None, None, get_report_summary(0, 0, 0, precision)

    # Create mappings
    invoice_totals = {inv.invoice: inv.grand_total for inv in valid_invoices}
    invoice_customers = {inv.invoice: inv.customer for inv in valid_invoices}
    invoice_customer_names = {inv.invoice: inv.customer_name for inv in valid_invoices}
    invoice_salespersons = {inv.invoice: inv.sales_person for inv in valid_invoices}
    invoice_set = set(invoice_totals.keys())

    if not invoice_set:
        return get_columns(), [], None, None, get_report_summary(0, 0, 0, precision)

    # Convert to tuple for SQL IN clause
    invoice_tuple = tuple(invoice_set)
    if len(invoice_tuple) == 1:
        invoice_tuple = f"('{invoice_tuple[0]}')"

    # Get PREVIOUS payments (before from_date)
    prev_payments_pe = []
    prev_payments_je = []
    
    if from_date:
        prev_payments_pe = frappe.db.sql("""
            SELECT
                pei.reference_name AS invoice,
                SUM(pei.allocated_amount) AS allocated_amount
            FROM `tabPayment Entry` pe
            INNER JOIN `tabPayment Entry Reference` pei ON pe.name = pei.parent
            WHERE pe.docstatus = 1
            AND pei.reference_doctype = 'Sales Invoice'
            AND pe.posting_date < %(from_date)s
            AND pei.reference_name IN %(invoice_tuple)s
            GROUP BY pei.reference_name
        """, {"from_date": from_date, "invoice_tuple": invoice_tuple}, as_dict=1)

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
            AND jea.reference_name IN %(invoice_tuple)s
            GROUP BY jea.reference_name
        """, {"from_date": from_date, "invoice_tuple": invoice_tuple}, as_dict=1)

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
        AND pei.reference_name IN %(invoice_tuple)s
        ORDER BY pe.posting_date, pe.name
    """, {"from_date": from_date, "to_date": to_date, "invoice_tuple": invoice_tuple}, as_dict=1)

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
        AND jea.reference_name IN %(invoice_tuple)s
        ORDER BY je.posting_date, je.name
    """, {"from_date": from_date, "to_date": to_date, "invoice_tuple": invoice_tuple}, as_dict=1)

    all_payments = payments + journals

    if not all_payments:
        return get_columns(), [], None, None, get_report_summary(0, 0, 0, precision)

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
    paid_cumulative = {}
    data = []

    for date in sorted_dates:
        daily_payments = payments_by_date[date]

        for pay in daily_payments:
            invoice = pay["invoice"]
            allocated_amt = flt(pay["allocated_amount"])
            pe_reference = pay["pe_reference"]
            sales_person = invoice_salespersons.get(invoice, 'N/A')
            customer_name = invoice_customer_names.get(invoice, 'N/A')

            previous_paid = previous_paid_map.get(invoice, 0)
            paid_before_today = paid_cumulative.get(invoice, 0)
            total_paid_till_now = previous_paid + paid_before_today + allocated_amt
            grand_total = invoice_totals.get(invoice, 0)
            outstanding = max(grand_total - total_paid_till_now, 0)

            data.append({
                "date": date,
                "customer": invoice_customers.get(invoice, 'N/A'),
                "customer_name": customer_name,
                "sales_person": sales_person,
                "si_reference": invoice,
                "pe_reference": pe_reference,
                "grand_total": round(flt(grand_total), int(precision)),
                "previous_allocated_amount": round(flt(previous_paid), int(precision)),
                "allocated_amount": round(flt(allocated_amt), int(precision)),
                "outstanding_amount": round(flt(outstanding), int(precision))
            })

            paid_cumulative[invoice] = paid_before_today + allocated_amt

    # Calculate totals
    total_grand = round(flt(sum(d["grand_total"] for d in data)), int(precision))
    total_paid = round(flt(sum(d["allocated_amount"] for d in data)), int(precision))
    total_outstanding = round(flt(sum(d["outstanding_amount"] for d in data)), int(precision))

    # Generate chart data
    chart_data = get_chart_data(data, precision)

    return get_columns(), data, None, chart_data, get_report_summary(total_grand, total_paid, total_outstanding, precision)

def get_columns():
    """Define report columns"""
    return [
        {
            "label": "Date",
            "fieldname": "date",
            "fieldtype": "Date",
            "width": 110
        },
        {
            "label": "Customer",
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 400
        },
        {
            "label": "Sales Person",
            "fieldname": "sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 200
        },
        {
            "label": "Sales Invoice",
            "fieldname": "si_reference",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 160
        },
        {
            "label": "Payment Entry",
            "fieldname": "pe_reference",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Grand Total",
            "fieldname": "grand_total",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "Prev. Allocated",
            "fieldname": "previous_allocated_amount",
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "label": "Allocated Amt.",
            "fieldname": "allocated_amount",
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "label": "Outstanding Amount",
            "fieldname": "outstanding_amount",
            "fieldtype": "Currency",
            "width": 180
        }
    ]

def get_chart_data(data, precision):
    """Generate chart data for visualization"""
    if not data:
        return None

    # Group data by date for chart
    daily_data = {}
    for row in data:
        date_str = row["date"].strftime('%Y-%m-%d')
        if date_str not in daily_data:
            daily_data[date_str] = {
                "invoiced": 0,
                "allocated": 0,
                "outstanding": 0
            }
        
        daily_data[date_str]["invoiced"] += flt(row["grand_total"])
        daily_data[date_str]["allocated"] += flt(row["allocated_amount"])
        daily_data[date_str]["outstanding"] += flt(row["outstanding_amount"])

    sorted_dates = sorted(daily_data.keys())
    
    return {
        "data": {
            "labels": [datetime.strptime(date, '%Y-%m-%d').strftime('%d-%m-%Y') for date in sorted_dates],
            "datasets": [
                {
                    "name": "Total Invoiced",
                    "values": [round(flt(daily_data[date]["invoiced"]), int(precision)) for date in sorted_dates]
                },
                {
                    "name": "Allocated Amount", 
                    "values": [round(flt(daily_data[date]["allocated"]), int(precision)) for date in sorted_dates]
                },
                {
                    "name": "Outstanding",
                    "values": [round(flt(daily_data[date]["outstanding"]), int(precision)) for date in sorted_dates]
                }
            ]
        },
        "type": "bar",
        "height": 300,
        "colors": ["#5e64ff", "#28a745", "#ff4d4d"]
    }

def get_report_summary(total_grand, total_paid, total_outstanding, precision):
    """Generate report summary"""
    currency = frappe.defaults.get_global_default("currency") or "BHD"
    
    # Ensure precision is an integer
    precision = int(precision) if precision else 3
    
    return [
        {
            "value": f"{round(flt(total_grand), precision)} {currency}",
            "label": "Total Invoiced",
            "datatype": "Currency"
        },
        {
            "value": f"{round(flt(total_paid), precision)} {currency}",
            "label": "Total Allocated",
            "datatype": "Currency"
        },
        {
            "value": f"{round(flt(total_outstanding), precision)} {currency}",
            "label": "Total Outstanding",
            "datatype": "Currency"
        }
    ]
import frappe
from erpnext.accounts.party import get_dashboard_info

@frappe.whitelist()
def get_unpaid_amt(customer, company):
    data = get_dashboard_info("Customer", customer)
    for i in data:
        if(i.get("company") == company):
            return i.get("currency") + " " + str(i.get("total_unpaid"))
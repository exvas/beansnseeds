# Copyright (c) 2024, sammish and contributors
# For license information, please see license.txt

import frappe
def get_columns():
	return [
		{"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": "120"},
		{"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data","width": "300"},
		{"label": "Invoice Number", "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": "200"},
		{"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": "200"},
		{"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": "250"},
		{"label": "UOM", "fieldname": "uom", "fieldtype": "Link","options":"UOM", "width": "120"},
		{"label": "Rate", "fieldname": "rate", "fieldtype": "Float", "width": "120"},
		{"label": "Stock UOM", "fieldname": "stock_uom", "fieldtype": "Link","options":"UOM", "width": "110"},
		{"label": "UOM Conversion Factor", "fieldname": "conversion_factor", "fieldtype": "Float", "width": "200"},
		{"label": "Qty As Per the Conversion", "fieldname": "stock_qty", "fieldtype": "Float", "width": "200"},
		{"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link","options":"Warehouse", "width": "150"},
	]

def execute(filters=None):
	columns, data = get_columns(), []

	conditions = ""
	if filters.get("from_date") and filters.get("to_date"):
		conditions += " and SI.posting_date BETWEEN '{0}' and '{1}' ".format(filters.get("from_date"),filters.get("to_date"))

	if len(filters.get("sales_invoice")) == 1:
		conditions += " and SI.name='{0}' ".format(filters.get("sales_invoice")[0])
	elif len(filters.get("sales_invoice")) > 1:
		conditions += " and SI.name in {0} ".format(tuple(filters.get("sales_invoice")))

	data = frappe.db.sql(""" SELECT SI.name as sales_invoice,SI.posting_date,SI.customer_name, SII.* FROM `tabSales Invoice` SI 
							INNER JOIN `tabSales Invoice Item` SII ON SII.parent = SI.name
							WHERE SI.docstatus=1 {0}
							""".format(conditions),as_dict=1)
	return columns, data

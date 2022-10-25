# Copyright (c) 2022, sammish and contributors
# For license information, please see license.txt
import frappe
from frappe import _, msgprint
def execute(filters=None):
	columns, data = [], []
	columns=get_columns()
	conditions=get_conditions(filters)
	lists=get_lists(filters)
	for li in lists:
		row=frappe._dict({
				'item_code':li.item_code,
				'item_name':li.item_name,
				'available_stock':li.available_stock,
				'valuation_rate':li.valuation_rate,
				'last_purchase_rate':li.last_purchase_rate,
				'landed_cost_rate':li.landed_cost_rate,
				'in_warehouse_rate':li.in_warehouse_rate,
				'purchase_rate':li.purchase_rate,
				'selling_rate':li.selling_rate,
				'profit_per_qty':li.profit_per_qty,
				'profit_percentage_qty':li.profit_percentage_qty,
				'profit_amount':li.profit_amount,
				'profit_percentage_amount':li.profit_percentage_amount,
				'selling_price_list':li.selling_price_list,
				'purchase_price_list':li.purchase_price_list,
				'company':li.company,			
			})	
		data.append(row)
	return columns,data

def get_columns():
	return[
		{
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options":"Item",
			"label": "Item Code",	
				

		},
		{
			"fieldname": "item_name",
			"fieldtype": "Data",
			"label": "Item Name",
			
		},
		{
			"fieldname": "available_stock",
			"fieldtype": "Float",
			"label": "Available Stock",
			"width":120,
			
			
		},
		{
			"fieldname": "valuation_rate",
			"fieldtype": "Currency",
			"label": "Valuation Rate",
			"width":120,
			
		},
		{
			"fieldname": "last_purchase_rate",
			"fieldtype": "Currency",
			"label": "Last Purchase Rate",
			"width":120, 
			
		},
		{
			"fieldname": "landed_cost_rate",
			"fieldtype": "Currency",
			"label": "Landed Cost Rate",
			"width":120, 
		
		},	
		{
			"fieldname": "in_warehouse_rate",
			"fieldtype": "Currency",
			"label": "In Warehouse Rate",
			"width":120, 
		
		},	
		{
			"fieldname": "purchase_rate",
			"fieldtype": "Currency",
			"label": "Purchase Rate",
			"width":120,
			
		},
		{
			"fieldname": "selling_rate",
			"fieldtype": "Currency",
			"label": "Selling Rate",
			"width":120,
	
		},
		{
			"fieldname": "profit_per_qty",
			"fieldtype": "Currency",
			"label": "Profit Per / Qty",
			"width":120,

		},
		{
			"fieldname": "profit_percentage_qty",
			"fieldtype": "Currency",
			"label": "Profit % per Qty",
			"width":120,
			
		},
		{
			"fieldname": "profit_amount",
			"fieldtype": "Currency",
			"label": "Profit Amount",
			"width":120,
		
		},
		{
			"fieldname": "selling_price_list",
			"fieldtype": "Data",
			"label": "Selling Price List",
			"width":120 
		},
		{
			"fieldname": "purchase_price_list",
			"fieldtype": "Data",
			"label": "Purchase Price List",
			"width":120 
		},
		{
			"fieldname": "company",
			"fieldtype": "Link",
			"label": "Company",
			"options":'Company',
			"width":120 
		},
		
	]

def get_lists(filters):
	conditions=get_conditions(filters)
	data=[]
	parent=frappe.db.sql("""select i.item_code,i.item_name,i.last_purchase_rate,s.valuation_rate,
	s.qty_after_transaction as available_stock from `tabItem` as i INNER JOIN `tabStock Ledger Entry` as s
	ON i.item_code=s.item_code GROUP BY item_code""",as_dict=1)
	for j in parent:
		j["indent"]=0
		filters=conditions
		data.append(j)
	return data
	# parent=frappe.db.sql("""SELECT i.item_name,i.last_purchase_rate,i.name,s.posting_date,
	# s.valuation_rate,
	# s.item_code,s.company,s.qty_after_transaction as available_stock from `tabItem` AS i 
	# INNER JOIN `tabItem Default` AS id ON i.name=id.parent INNER JOIN `tabStock Ledger Entry`
	# as s ON i.name=s.item_code GROUP BY s.item_code {0}""".format(conditions),as_dict=1)
	# for i in parent:
	# 	i["indent"] = 0
	# 	filters=conditions
	# 	i.update(i)	
	# 	i_code=i.get('item_code')
		# stock_data=frappe.db.sql("""select posting_date,qty_after_transaction as available_stock,valuation_rate from
		# `tabStock Ledger Entry` where item_code=%s {0}""".format(conditions),i_code,as_dict=1 )
		# if stock_data:
		# 	for j in stock_data:		
		# 		j["indent"] = 0
		# 		filters=conditions
		# 		i.update(j)
		# Landed_data=frappe.db.sql("""select applicable_charges as landed_cost_rate from 
		# `tabLanded Cost Item` where item_code=%s """,i_code,as_dict=1)
		# if Landed_data:
		# 	for k in Landed_data:
		# 		k["indent"]=0
		# 		filters=conditions
		# 		i.update(k)

		# selling_rate_data=frappe.db.sql("""select price_list as selling_price_list ,
		# price_list_rate as selling_rate from `tabItem Price` where item_code=%s and 
		# selling=1 """,i_code,as_dict=1)
		# if selling_rate_data:
		# 	for l in selling_rate_data:
		# 		l["indent"]=0
		# 		filters=conditions
		# 		i.update(l)

		# purchase_rate_data=frappe.db.sql("""select price_list as purchase_price_list ,
		# price_list_rate as purchase_rate from `tabItem Price` where item_code=%s and 
		# buying=1 """,i_code,as_dict=1)
		# if purchase_rate_data:
		# 	for m in purchase_rate_data:
		# 		m["indent"]=0
		# 		filters=conditions
		# 		i.update(m)

		# if i.last_purchase_rate and i.landed_cost_rate:
		# 	w={'in_warehouse_rate':i .last_purchase_rate+i.landed_cost_rate}
		# 	i.update(w)
		# if i.selling_rate and i .in_warehouse_rate:
		# 	p={'profit_per_qty':i.selling_rate-i.in_warehouse_rate}
		# 	i.update(p)
		# if i.selling_rate and i.in_warehouse_rate:
		# 	a={'profit_percentage_qty':i.in_warehouse_rate/i.selling_rate*100}
		# 	i.update(a)
		# if i.profit_per_qty and i.available_stock:
		# 	pp={'profit_amount':i.profit_per_qty*i.available_stock}
		# 	i.update(pp)


	# return parent

# def get_lists(filters):
# 	conditions=get_conditions(filters)
# 	data=[]
# 	parent=frappe.db.sql("""SELECT 
# 	i.item_code,i.item_name,i.last_purchase_rate,i.name,id.company from `tabItem` AS i 
# 	INNER JOIN `tabItem Default` AS id ON i.name=id.parent {0}""".format(conditions),as_dict=1)
	
# 	for i in parent:
# 		i["indent"] = 0
# 		filters=conditions
# 		data.append(i)	
# 		i_code=i.get('item_code')
# 		stock_data=frappe.db.sql("""select posting_date,qty_after_transaction as available_stock,valuation_rate from
# 		`tabStock Ledger Entry` where item_code=%s {0}""".format(conditions),i_code,as_dict=1 )
# 		if stock_data:
# 			for j in stock_data:		
# 				j["indent"] = 0
# 				filters=conditions
# 				i.update(j)
# 		# else:
# 		# 	d={'available_stock':0,'valuation_rate':0}
# 		# 	print(d)
# 		# 	i.update(d)
# 		Landed_data=frappe.db.sql("""select applicable_charges as landed_cost_rate from 
# 		`tabLanded Cost Item` where item_code=%s """,i_code,as_dict=1)
# 		if Landed_data:
# 			for k in Landed_data:
# 				k["indent"]=0
# 				filters=conditions
# 				i.update(k)

# 		selling_rate_data=frappe.db.sql("""select price_list as selling_price_list ,
# 		price_list_rate as selling_rate from `tabItem Price` where item_code=%s and 
# 		selling=1 """,i_code,as_dict=1)
# 		if selling_rate_data:
# 			for l in selling_rate_data:
# 				l["indent"]=0
# 				filters=conditions
# 				i.update(l)

# 		purchase_rate_data=frappe.db.sql("""select price_list as purchase_price_list ,
# 		price_list_rate as purchase_rate from `tabItem Price` where item_code=%s and 
# 		buying=1 """,i_code,as_dict=1)
# 		if purchase_rate_data:
# 			for m in purchase_rate_data:
# 				m["indent"]=0
# 				filters=conditions
# 				i.update(m)

# 		if i.last_purchase_rate and i.landed_cost_rate:
# 			w={'in_warehouse_rate':i .last_purchase_rate+i.landed_cost_rate}
# 			i.update(w)
# 		if i.selling_rate and i .in_warehouse_rate:
# 			p={'profit_per_qty':i.selling_rate-i.in_warehouse_rate}
# 			i.update(p)
# 		if i.selling_rate and i.in_warehouse_rate:
# 			a={'profit_percentage_qty':i.in_warehouse_rate/i.selling_rate*100}
# 			i.update(a)
# 		if i.profit_per_qty and i.available_stock:
# 			pp={'profit_amount':i.profit_per_qty*i.available_stock}
# 			i.update(pp)


# 	return data

def get_conditions(filters):
	conditions=[]
	# conditions={'status':('=',filters.get('status'))}
	
	if filters.get("company"):
		conditions += " and company='{0}' ".format(filters.get("company"))
	if filters.get("item_code"):
		conditions += " and item_code='{0}' ".format(filters.get("item_code"))
	if filters.get("posting_date"):
		conditions += " and posting_date='{0}' ".format(filters.get("posting_date"))

	return conditions
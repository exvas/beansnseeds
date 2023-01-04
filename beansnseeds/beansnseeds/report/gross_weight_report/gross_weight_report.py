# Copyright (c) 2022, sammish and contributors
# For license information, please see license.txt
import frappe
from frappe import _, msgprint
def execute(filters=None):
	columns, data = [], []
	columns=get_columns()
	c=get_conditions(filters)
	lists=get_lists(filters)
	
	for li in lists:
		row=frappe._dict({
			'item_code':li.item_code,
			'item_name':li.item_name,
			'uom':li.uom,
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
			# 'company':li.company,			
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
			"fieldname": "uom",
			"fieldtype": "Link",
			"options":"UOM",
			"label": "UOM",
			
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
		# {
		# 	"fieldname": "company",
		# 	"fieldtype": "Link",
		# 	"label": "Company",
		# 	"options":'Company',
		# 	"width":120 
		# },
		
	]
def get_lists(filters):
	c=get_conditions(filters)
	data=[]
	if filters.get('company') and filters.get('from_date') and filters.get('to_date'):
		items=frappe.db.sql(""" SELECT item_code from `tabItem`""",as_dict=1)
		for it in items:
			p=frappe.db.sql("""select s.valuation_rate,s.qty_after_transaction as available_stock,s.posting_date,i.item_code,
			i.item_name,i.stock_uom as uom,i.last_purchase_rate,id.company from `tabStock Ledger Entry` as s 
			INNER JOIN `tabItem` as i ON i.item_code=s.item_code INNER JOIN `tabItem Default` as id 
			ON i.name=id.parent where i.item_code=%s and s.is_cancelled=0 {0} ORDER BY posting_date desc,posting_time desc limit 1""".format(c),it.item_code,as_dict=1)
			for i in p:
				i["indent"]=0
				filters=c
				data.append(i)
				Landed_data=frappe.db.sql("""select c.applicable_charges,c.qty from
				`tabLanded Cost Voucher` as l INNER JOIN  
				`tabLanded Cost Item` as c where c.item_code=%s and l.name=c.parent order by l.posting_date desc limit 1""",it.item_code,as_dict=1)
				if Landed_data:
					for k in Landed_data:
						landed_rate={'landed_cost_rate':k.applicable_charges/k.qty}
						k["indent"]=0
						filters=c
						i.update(landed_rate)

				selling_rate_data=frappe.db.sql("""select price_list as selling_price_list ,
				price_list_rate as selling_rate from `tabItem Price` where item_code=%s and 
				selling=1 """,it.item_code,as_dict=1)
				if selling_rate_data:
					for l in selling_rate_data:
						l["indent"]=0
						filters=c
						i.update(l)

				purchase_rate_data=frappe.db.sql("""select price_list as purchase_price_list ,
				price_list_rate as purchase_rate from `tabItem Price` where item_code=%s and 
				buying=1 """,it.item_code,as_dict=1)
				if purchase_rate_data:
					for m in purchase_rate_data:
						m["indent"]=0
						filters=c
						i.update(m)

				if i.last_purchase_rate and i.landed_cost_rate:
					w={'in_warehouse_rate':i .last_purchase_rate+i.landed_cost_rate}
					i.update(w)
				if i.selling_rate and i .in_warehouse_rate:
					p={'profit_per_qty':i.selling_rate-i.in_warehouse_rate}
					i.update(p)
				if i.selling_rate and i.in_warehouse_rate:
					a={'profit_percentage_qty':i.in_warehouse_rate/i.selling_rate*100}
					i.update(a)
				if i.profit_per_qty and i.available_stock:
					pp={'profit_amount':i.profit_per_qty*i.available_stock}
					i.update(pp)


		return data

	

def get_conditions(filters):
	c=""
	if filters.get("from_date") and filters.get("to_date"):
		c += "and posting_date BETWEEN '{0}' and '{1}' ".format(filters.get("from_date"),filters.get("to_date"))
		if filters.get("company"):
			c += "and id.company='{0}' ".format(filters.get("company"))
		if filters.get("item_code"):
			c += " and i.item_code='{0}' ".format(filters.get("item_code"))	
	if filters.get("company"):
		c += "and id.company='{0}' ".format(filters.get("company"))
	if filters.get("item_code"):
		c += " and i.item_code='{0}' ".format(filters.get("item_code"))
	return c

		
	
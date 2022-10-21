// Copyright (c) 2022, sammish and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Sales Report"] = {
	"filters": [
		{
			"fieldname": "sales_person",
			"fieldtype": "Link",
			"label": "Sales Person",
			"options": "Sales Person"
		
		},
		{
			
			"fieldname": "from_date",
			"fieldtype": "Date",
			"label": "From Date",
		},
		{			
			"fieldname": "to_date",
			"fieldtype": "Date",
			"label": "To Date",			
		},
		
	

	]
};
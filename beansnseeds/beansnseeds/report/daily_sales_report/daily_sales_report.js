// Copyright (c) 2022, sammish and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Sales Report"] = {
	"filters": [
		{
			"fieldname": "sales_person",
			"fieldtype": "Link",
			"label": "Sales Person",
			"options": "Sales Person",
			"reqd":1,
		
		},
		{			
			"fieldname": "company",
			"fieldtype": "Link",
			"label": "Company",
			"options": "Company",
			// "reqd":1,		
		},
		{
			
			"fieldname": "from_date",
			"fieldtype": "Date",
			"label": "From Date",
			// "reqd":1,
		},
		{			
			"fieldname": "to_date",
			"fieldtype": "Date",
			"label": "To Date",	
			// "reqd":1,		
		},
		
	

	]
};
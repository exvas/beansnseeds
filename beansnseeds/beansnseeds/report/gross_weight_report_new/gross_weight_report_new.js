// Copyright (c) 2022, sammish and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Gross Weight Report New"] = {
	"filters": [
		{
			"fieldname": "company",
			"fieldtype": "Link",
			"label": "Company",
			"options": "Company"
		
		},
		{
			
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"label": "Date",
		},
		{			
			"fieldname": "item_code",
			"fieldtype": "Link",
			"label": "Item",
			"options":"Item",			
		},
		// {			
		// 	"fieldname": "ignore_zero_stock",
		// 	"fieldtype": "Check",
		// 	"label": "Ignore Zero Stock",			
		// },
		// {			
		// 	"fieldname": "ignore_negative_stock",
		// 	"fieldtype": "Check",
		// 	"label": "Ignore Negative Stock",			
		// },


	]
};

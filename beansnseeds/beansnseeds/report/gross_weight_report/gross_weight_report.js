// Copyright (c) 2022, sammish and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Gross Weight Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"fieldtype": "Link",
			"label": "Company",
			"options": "Company",
			"reqd":1,
		
		},
		{
			
			"fieldname": "from_date",
			"fieldtype": "Date",
			"label": "From Date",
			"reqd":1,
		},
		{
			
			"fieldname": "to_date",
			"fieldtype": "Date",
			"label": "To Date",
			"reqd":1,
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

// Copyright (c) 2024, sammish and contributors
// For license information, please see license.txt

frappe.query_reports["Update Sales Stock Report"] = {
	"filters": [
		{
			fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
		},
		{
			fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
		},
		{
			"fieldname":"sales_invoice",
			"label": __("Sales Invoice"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {

				return frappe.db.get_link_options("Sales Invoice", txt);
			},
		},
		{
			"fieldname":"warehouse",
			"label": __("Warehouse"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {

				return frappe.db.get_link_options("Warehouse", txt);
			},
		},
		{
			"fieldname":"sales_person",
			"label": __("Sales Person"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {

				return frappe.db.get_link_options("Sales Person", txt);
			},
		}
	]
};

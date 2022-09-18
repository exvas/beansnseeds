// Copyright (c) 2022, sammish and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock List Report"] = {
	"filters": [
		{
			fieldname: "date",
            label: __("Date"),
            fieldtype: "Date",
			reqd: 1
		},
		{
			fieldname: "item_group",
            label: __("Item Group"),
            fieldtype: "Link",
            options: "Item Group",
			reqd: 1
		},
		{
			fieldname: "item",
            label: __("Item"),
            fieldtype: "Link",
            options: "Item",
			get_query: function () {
				var item_group = frappe.query_report.get_filter_value('item_group');
				return {
					filters: {
						item_group: item_group
					}
				}
            }
		},
		{
			fieldname: "ignore_zero_stock",
            label: __("Ignore Zero Stock"),
            fieldtype: "Check"
		},
		{
			fieldname: "ignore_negative_stock",
            label: __("Ignore Negative Stock"),
            fieldtype: "Check"
		}
	]
};
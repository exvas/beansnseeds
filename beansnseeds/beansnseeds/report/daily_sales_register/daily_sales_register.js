// Copyright (c) 2025, sammish and contributors
// For license information, please see license.txt

frappe.query_reports["Daily Sales Register"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        },
        {
            "fieldname": "sales_person",
            "label": __("Sales Person"),
            "fieldtype": "Link",
            "options": "Sales Person",
            "reqd": 1
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1,
            "width": "60px"
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1,
            "width": "60px"
        },
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
            "width": "100px",
            "get_query": function() {
                return {
                    "doctype": "Customer",
                    "filters": {
                        "disabled": 0
                    }
                };
            }
        }
    ],

    "formatter": function(value, row, column, data, default_formatter) {
        // Get currency precision from system settings (default to 3)
        let precision = frappe.boot.sysdefaults.currency_precision || 3;
        
        // Handle currency formatting with system precision
        if (column.fieldtype === "Currency" && value !== null && value !== undefined && value !== "") {
            let currency = frappe.defaults.get_default("currency") || "BHD";
            let num_value = flt(value);
            let formatted_value = num_value.toFixed(precision);
            value = `${formatted_value} ${currency}`;
        } else {
            value = default_formatter(value, row, column, data);
        }

        // Highlight outstanding amounts in red
        if (column.fieldname === "outstanding_amount" && data && flt(data.outstanding_amount) > 0) {
            value = `<span style='color: red; font-weight: bold;'>${value}</span>`;
        }

        // Highlight allocated amounts in green
        if (column.fieldname === "allocated_amount" && data && flt(data.allocated_amount) > 0) {
            value = `<span style='color: green; font-weight: bold;'>${value}</span>`;
        }

        // Highlight previous allocated amounts in blue
        if (column.fieldname === "previous_allocated_amount" && data && flt(data.previous_allocated_amount) > 0) {
            value = `<span style='color: blue; font-weight: bold;'>${value}</span>`;
        }

        // Make Customer clickable and display customer name
        if (column.fieldname === "customer" && data && data.customer) {
            let display_text = data.customer;
            if (data.customer_name && data.customer_name !== data.customer) {
                display_text = `${data.customer} - ${data.customer_name}`;
            }
            value = `<a href="/app/customer/${data.customer}" target="_blank" style="text-decoration: underline;">${display_text}</a>`;
        }

        // Make Customer Name display
        if (column.fieldname === "customer_name" && data && data.customer_name) {
            value = `<span>${data.customer_name}</span>`;
        }

        // Make SI Reference clickable
        if (column.fieldname === "si_reference" && data && data.si_reference) {
            value = `<a href="/app/sales-invoice/${data.si_reference}" target="_blank" style="text-decoration: underline;">${data.si_reference}</a>`;
        }

        // Make PE Reference clickable
        if (column.fieldname === "pe_reference" && data && data.pe_reference) {
            if (data.pe_reference.startsWith('ACC-PAY')) {
                value = `<a href="/app/payment-entry/${data.pe_reference}" target="_blank" style="text-decoration: underline;">${data.pe_reference}</a>`;
            } else {
                value = `<a href="/app/journal-entry/${data.pe_reference}" target="_blank" style="text-decoration: underline;">${data.pe_reference}</a>`;
            }
        }

        return value;
    },

    "onload": function(report) {
        // Add custom buttons to the report
        report.page.add_inner_button(__("Export to Excel"), function() {
            frappe.query_report.export_report('Excel', 'Daily Sales Register');
        });

        report.page.add_inner_button(__("Export to PDF"), function() {
            frappe.query_report.export_report('PDF', 'Daily Sales Register');
        });

        report.page.add_inner_button(__("Print"), function() {
            frappe.query_report.print_report();
        });

        report.page.add_inner_button(__("Refresh"), function() {
            report.refresh();
        }, __("Actions"));

        // Set report title dynamically
        let title = __("Daily Sales Register");
        if (report.filters && report.filters.length > 0) {
            let company = report.get_filter_value('company');
            if (company) {
                title += ` - ${company}`;
            }
        }
        report.page.set_title(title);
    },

    "after_datatable_render": function(datatable_obj) {
        // Add total row at the bottom
        let data = frappe.query_report.data;
        if (data && data.length > 0) {
            let total_grand_total = 0;
            let total_outstanding = 0;
            let total_allocated = 0;

            data.forEach(function(row) {
                total_grand_total += flt(row.grand_total);
                total_outstanding += flt(row.outstanding_amount);
                total_allocated += flt(row.allocated_amount);
            });

            // Get currency precision from system settings
            let precision = frappe.boot.sysdefaults.currency_precision || 3;
            
            // Round totals to system precision
            total_grand_total = flt(total_grand_total).toFixed(precision);
            total_outstanding = flt(total_outstanding).toFixed(precision);
            total_allocated = flt(total_allocated).toFixed(precision);

            let currency = frappe.defaults.get_default("currency") || "BHD";

            // Add summary row
            let summary_row = {
                date: "",
                customer: "",
                customer_name: "<b>TOTAL</b>",
                sales_person: "",
                si_reference: "",
                pe_reference: "",
                grand_total: `<b>${total_grand_total} ${currency}</b>`,
                previous_allocated_amount: "",
                allocated_amount: `<b style='color: green;'>${total_allocated} ${currency}</b>`,
                outstanding_amount: `<b style='color: red;'>${total_outstanding} ${currency}</b>`
            };

            // Add the summary row to datatable
            setTimeout(function() {
                if (datatable_obj && datatable_obj.bodyRenderer && datatable_obj.bodyRenderer.addRow) {
                    datatable_obj.bodyRenderer.addRow(summary_row, data.length);
                }
            }, 100);
        }
    },

    "get_chart_data": function(columns, result) {
        // Generate chart data for visualization
        if (!result || result.length === 0) {
            return null;
        }

        let precision = frappe.boot.sysdefaults.currency_precision || 3;
        let monthly_data = {};

        result.forEach(function(row) {
            let month = moment(row.date).format('YYYY-MM');
            if (!monthly_data[month]) {
                monthly_data[month] = {
                    invoiced: 0,
                    allocated: 0,
                    outstanding: 0
                };
            }

            monthly_data[month].invoiced += flt(row.grand_total);
            monthly_data[month].allocated += flt(row.allocated_amount);
            monthly_data[month].outstanding += flt(row.outstanding_amount);
        });

        let labels = Object.keys(monthly_data).sort();
        let invoiced_data = labels.map(function(label) {
            return flt(monthly_data[label].invoiced).toFixed(precision);
        });
        let allocated_data = labels.map(function(label) {
            return flt(monthly_data[label].allocated).toFixed(precision);
        });
        let outstanding_data = labels.map(function(label) {
            return flt(monthly_data[label].outstanding).toFixed(precision);
        });

        return {
            data: {
                labels: labels.map(function(label) {
                    return moment(label + '-01').format('MMM YYYY');
                }),
                datasets: [
                    {
                        name: __("Total Invoiced"),
                        values: invoiced_data,
                        chartType: 'bar'
                    },
                    {
                        name: __("Total Allocated"),
                        values: allocated_data,
                        chartType: 'bar'
                    },
                    {
                        name: __("Outstanding"),
                        values: outstanding_data,
                        chartType: 'bar'
                    }
                ]
            },
            type: 'bar',
            height: 300,
            colors: ['#7cd6fd', '#28a745', '#ff6b6b']
        };
    },

    "tree": false,
    "name_field": "si_reference",
    "parent_field": "",
    "initial_depth": 0,

    "custom_format": function(value, row, column) {
        return value;
    }
};

// Utility functions
function format_currency(value, currency) {
    if (!currency) {
        currency = frappe.defaults.get_default("currency") || "BHD";
    }
    let precision = frappe.boot.sysdefaults.currency_precision || 3;
    return flt(value).toFixed(precision) + " " + currency;
}

// Add event listeners for filter changes
frappe.query_reports["Daily Sales Register"].on_filter_change = function() {
    console.log("Filters changed");
};

// Custom CSS for the report
frappe.provide('frappe.query_reports');
$(document).ready(function() {
    $('<style>')
        .prop('type', 'text/css')
        .html(`
            .query-report .datatable .dt-row .dt-cell {
                vertical-align: middle;
            }
            
            .query-report .datatable .dt-row:hover {
                background-color: #f8f9fa;
            }
            
            .query-report .report-summary {
                margin-bottom: 15px;
            }
            
            .report-summary .summary-item {
                display: inline-block;
                margin-right: 20px;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 5px;
                min-width: 150px;
                text-align: center;
            }
            
            .report-summary .summary-item .summary-label {
                font-size: 12px;
                color: #6c757d;
                margin-bottom: 5px;
            }
            
            .report-summary .summary-item .summary-value {
                font-size: 18px;
                font-weight: bold;
                color: #495057;
            }
            
            .dt-cell[data-fieldtype="Currency"] {
                text-align: right;
                font-family: monospace;
            }
        `)
        .appendTo('head');
});
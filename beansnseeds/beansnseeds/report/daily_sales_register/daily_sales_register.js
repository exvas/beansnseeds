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
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
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
            "width": "100px"
        }
    ],

    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Highlight overdue amounts in red
        if (column.fieldname == "outstanding_amount" && data && flt(data.outstanding_amount) > 0) {
            value = `<span style='color: red; font-weight: bold;'>${value}</span>`;
        }
        
        // Highlight paid amounts in green
        if (column.fieldname == "paid_amount" && data && flt(data.paid_amount) > 0) {
            value = `<span style='color: green; font-weight: bold;'>${value}</span>`;
        }
        
        // Make SI Reference clickable
        if (column.fieldname == "si_reference" && data && data.si_reference) {
            value = `<a href="/app/sales-invoice/${data.si_reference}" target="_blank">${data.si_reference}</a>`;
        }
        
        // Make PE Reference clickable
        if (column.fieldname == "pe_reference" && data && data.pe_reference) {
            if (data.pe_reference.startsWith('ACC-PAY')) {
                value = `<a href="/app/payment-entry/${data.pe_reference}" target="_blank">${data.pe_reference}</a>`;
            } else {
                value = `<a href="/app/journal-entry/${data.pe_reference}" target="_blank">${data.pe_reference}</a>`;
            }
        }
        
        return value;
    },

    "onload": function(report) {
        // Add custom buttons to the report
        report.page.add_inner_button(__("Export to Excel"), function() {
            frappe.query_report.export_report('Excel', 'Beans and Seeds Trad Report');
        });

        report.page.add_inner_button(__("Export to PDF"), function() {
            frappe.query_report.export_report('PDF', 'Beans and Seeds Trad Report');
        });

        report.page.add_inner_button(__("Print"), function() {
            frappe.query_report.print_report();
        });

        // Add a refresh button
        report.page.add_inner_button(__("Refresh"), function() {
            report.refresh();
        }, __("Actions"));
        
        // Set report title dynamically
        let title = __("Beans and Seeds Trading Report");
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
            let total_paid = 0;
            
            data.forEach(function(row) {
                total_grand_total += flt(row.grand_total);
                total_outstanding += flt(row.outstanding_amount);
                total_paid += flt(row.paid_amount);
            });
            
            // Add summary row
            let summary_row = {
                date: "",
                customer_name: "<b>Total</b>",
                si_reference: "",
                pe_reference: "",
                grand_total: `<b>${format_currency(total_grand_total)}</b>`,
                outstanding_amount: `<b style='color: red;'>${format_currency(total_outstanding)}</b>`,
                paid_amount: `<b style='color: green;'>${format_currency(total_paid)}</b>`
            };
            
            // Add the summary row to datatable
            setTimeout(function() {
                datatable_obj.bodyRenderer.addRow(summary_row, data.length);
            }, 100);
        }
    },

    "get_chart_data": function(columns, result) {
        // Generate chart data for visualization
        if (!result || result.length === 0) {
            return null;
        }

        let monthly_data = {};
        
        result.forEach(function(row) {
            let month = moment(row.date).format('YYYY-MM');
            if (!monthly_data[month]) {
                monthly_data[month] = {
                    invoiced: 0,
                    paid: 0,
                    outstanding: 0
                };
            }
            
            monthly_data[month].invoiced += flt(row.grand_total);
            monthly_data[month].paid += flt(row.paid_amount);
            monthly_data[month].outstanding += flt(row.outstanding_amount);
        });

        let labels = Object.keys(monthly_data).sort();
        let invoiced_data = labels.map(function(label) {
            return monthly_data[label].invoiced;
        });
        let paid_data = labels.map(function(label) {
            return monthly_data[label].paid;
        });
        let outstanding_data = labels.map(function(label) {
            return monthly_data[label].outstanding;
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
                        name: __("Total Paid"),
                        values: paid_data,
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
            colors: ['#7cd6fd', '#5e64ff', '#ff6b6b']
        };
    },

    // Custom function to handle row click events
    "tree": false,
    "name_field": "si_reference",
    "parent_field": "",
    "initial_depth": 0,

    // Add custom styling
    "custom_format": function(value, row, column) {
        // Custom formatting logic can be added here
        return value;
    }
};

// Utility functions
function format_currency(value, currency) {
    if (!currency) {
        currency = frappe.defaults.get_default("currency");
    }
    return format_number(value, null, 2) + " " + currency;
}

// Add event listeners for filter changes
frappe.query_reports["Beans and Seeds Trad Report"].on_filter_change = function() {
    // Custom logic when filters change
    console.log("Filters changed");
};

// Custom CSS for the report
frappe.provide('frappe.query_reports');
$(document).ready(function() {
    // Add custom CSS
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
        `)
        .appendTo('head');
});
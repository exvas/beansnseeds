frappe.ui.form.on("Sales Invoice", {
    customer(frm){
        if(frm.doc.customer && frm.doc.company){
            frappe.call({
                method: "beansnseeds.api.customer.get_unpaid_amt",
                args: {
                    customer: frm.doc.customer,
                    company: frm.doc.company
                },
                callback:function(r){
                    if(r.message){
                        frm.doc.custom_unpaid_amount = `<p style='font-size:18px;'>${r.message}</p>`
                        frm.refresh_field("custom_unpaid_amount")
                    }
                }
            })
        }
    }
})
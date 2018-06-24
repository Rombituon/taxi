// Copyright (c) 2017, Bilal Ghayad and contributors
// For license information, please see license.txt

frappe.ui.form.on('Trip Order', {
	refresh: function(frm) {

//		var me = this;
//		this._super();


//		cur_frm.add_custom_button(__('Invoice'), this.make_sales_invoice, __("Make"));


		frm.add_custom_button(__('Invoice'),
			function() { frm.events.make_sales_invoice(frm); }, __("Make"));

		frm.add_custom_button(__('Payment'),
			function() { frm.events.make_payment_entry(frm); }, __("Make"));
 
//        	this.frm.add_custom_button(__('Invoice'), 
//			function() { me.make_sales_invoice() }, __("Make"));
 	
//		frm.set_value('hop_no_discounted', '2');
//		cur_frm.doc.hop_no_discounted = '2';
	},


        onload: function(frm) {
                frm.set_query("assigned_driver", function(doc) {
                        return {
                                filters: {
                                        'status': 'Active'
                                }
                        };
                });
	},

        make_payment_entry: function(frm) {
		return frappe.call({
                        method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_payment_entry",
                        args: {
                                "dt": frm.doc.doctype,
                                "dn": frm.doc.name
                        },
                        callback: function(r) {
//				frappe.msgprint(__("Payment Submitted Successfully"));
                                var doc = frappe.model.sync(r.message);
                                frappe.set_route("Form", doc[0].doctype, doc[0].name);
                        }
                });
        },

        make_sales_invoice: function(frm) {
                return frappe.call({
                        method: "taxi.taxi.doctype.trip_order.trip_order.make_sales_invoice",
                        args: {
                                "dt": frm.doc.doctype,
                                "dn": frm.doc.name
                        },
                        callback: function(r) {
//                              frappe.msgprint(__("Payment Submitted Successfully"));
                                var doc = frappe.model.sync(r.message);
//                                frappe.set_route("Form", doc[0].doctype, doc[0].name);


                		frappe.call({
                        		method: "taxi.taxi.doctype.trip_order.trip_order.make_payment_entry",
                        		args: {
                                	"si_dn": doc[0].name,
                                	"to_dn": frm.doc.name
                        	},
				callback: function(r) {
                                	var payment_doc = frappe.model.sync(r.message);
                                	frappe.set_route("Form", payment_doc[0].doctype, payment_doc[0].name);
				}
                        	})
			}
                });
        }

});

//taxi.taxi.TripOrderController = taxi.taxi.TaxiController.extend({
//        refresh: function(doc, cdt, cdn) {
//                var me = this;
//                this._super();
//                this.frm.add_custom_button(__('Invoice'),
//                        function() { me.frm.make_sales_invoice() }, __("Make"));
//        },
//        make_sales_invoice: function() {
//                frappe.model.open_mapped_doc({
//                        method: "taxi.taxi.doctype.trip_order.trip_order.make_sales_invoice",
//                        frm: this.frm
//                })
//        }
//});

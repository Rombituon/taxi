// Copyright (c) 2018, Bilal Ghayad and contributors
// For license information, please see license.txt

cur_frm.add_fetch('driver', 'employee_name', 'driver_name')
cur_frm.add_fetch('commission_rule', 'commission_percent', 'commission_percent')
cur_frm.add_fetch('commission_rule', 'weekly_fees', 'weekly_fees')
cur_frm.add_fetch('last_clearance', 'clearance_date', 'last_clearance_date')
//cur_frm.add_fetch('last_com_rule', 'commission_percent', 'last_com_percent')
//cur_frm.add_fetch('last_com_rule', 'weekly_fees', 'last_weekly_fees')
//cur_frm.add_fetch('last_assigned_commission_rule', 'active_date', 'last_acr_active_date')
//cur_frm.add_fetch('last_assigned_commission_rule', 'commission_rule', 'last_com_rule')
//cur_frm.add_fetch('last_assigned_commission_rule', 'commission_percent', 'last_com_percent')
//cur_frm.add_fetch('last_assigned_commission_rule', 'weekly_fees', 'last_weekly_fees')

frappe.ui.form.on('Assign Commission Rule', {
	refresh: function(frm) {

	},
	driver: function(frm) {

                if (cur_frm.doc.driver) {
		
			frappe.call({
				method: "taxi.taxi.doctype.assign_commission_rule.assign_commission_rule.get_values",
				args: {
					"AssignedDriver": frm.doc.driver
				},
                        	callback: function(r) {
					if (r.message) {

						if (r.message[0].length) {

							frappe.msgprint(__("The joining date is: {0}", [r.message[3]]));
							frappe.msgprint(__("Last Clearance Date: {0}", [r.message[0]]));
							var last_clr = r.message[0];
                                                	cur_frm.set_value("last_clearance", last_clr[0]['name']);
                                                	cur_frm.set_value("last_clearance_date", last_clr[0]['clearance_date']);

							cur_frm.set_value("is_there_anyclr_before", '');
							cur_frm.set_value("date_of_joining", '');

							var clr_d1 = new Date (last_clr[0]['clearance_date']);
//							var d2 = new Date (last_clr[0]['clearance_date']);
                                      			frappe.msgprint(__("The minutes is: {0}", [clr_d1.getMinutes()]));
						
//							d1.setMinutes (d1.getMinutes() + 1);
							var clr_d2 = new Date();
							clr_d2.setTime(clr_d1.getTime() + (1 * 60 * 1000));
                                                	cur_frm.set_value("active_date", clr_d2);
							cur_frm.refresh();
//							refresh_field("last_clearance");
//							refresh_field("last_clearance_date");
						} else {
							frappe.msgprint(__("The joining date is: {0}", [r.message[3]]));
//							frappe.msgprint(__("Last assigned crl is: {0}", [r.message[1][0]['name']]));
							var hir_d1 = new Date (r.message[3]);
							hir_d1.setHours (00);
							hir_d1.setMinutes (01);
							hir_d1.setSeconds (00);
//							var hir_d2 = new Date();
//							hir_d2.setTime(hir_d1.getTime() + (1 * 60 * 1000));
							cur_frm.set_value("active_date", hir_d1);
							cur_frm.set_value("is_there_anyclr_before", "There is not any previous clearance for this driver.");
							cur_frm.set_value("date_of_joining", r.message[3]);
                                                	cur_frm.set_value("last_clearance", '');
                                                	cur_frm.set_value("last_clearance_date", '');
							cur_frm.refresh();
						};
						if (r.message[1].length) {
                                        		var last_assigned_crl = r.message[1];

							frappe.msgprint(__("Length for last assignment is: {0}", [r.message[1].length]));
                                                	cur_frm.set_value("last_assigned_commission_rule", last_assigned_crl[0]['name']);
                                                	cur_frm.set_value("last_acr_active_date", last_assigned_crl[0]['active_date']);
                                                	cur_frm.set_value("last_com_rule", last_assigned_crl[0]['commission_rule']);
                                                	cur_frm.set_value("last_com_percent", last_assigned_crl[0]['commission_percent']);
                                                	cur_frm.set_value("last_weekly_fees", last_assigned_crl[0]['weekly_fees']);
							cur_frm.refresh();
						}
						else {					
                                                	cur_frm.set_value("last_assigned_commission_rule", '');
                                                	cur_frm.set_value("last_acr_active_date", '');
                                                	cur_frm.set_value("last_com_rule", '');
                                                	cur_frm.set_value("last_com_percent", '');
                                                	cur_frm.set_value("last_weekly_fees", '');
						}
						cur_frm.refresh();

//                                      	frappe.msgprint(__("Welcome: {0}", [statement[0]['creation']]));
//                                      	frappe.msgprint(__("Last Payment: {0}", [last_payment[0]['creation']]));
//                                      	frappe.msgprint(__("Welcome"));
//                                      	frappe.msgprint(__("Welcome: {0}", [frappe.datetime.nowdate()]));
//                                      	cur_frm.set_value("clearance_date", frappe.datetime.nowdate());
//                                      	cur_frm.set_value("cash_with_him", r.message[1]);
//                                      	cur_frm.set_value("last_payment_date", last_payment[0]['creation']);
//                                      	cur_frm.set_value("last_clearance_date", r.message[3]);
//                                      	filling_and_calculation(frm, statement);
//                                      	cur_frm.set_value("vehicle", r.message);
                                	}

                        	}
                	});
		}
	},
	onload: function(frm) {
		frm.set_query("commission_rule", function(doc) {
                        return {
                                filters: {
                                        'docstatus': 1
                                }
			};
		});
                frm.set_query("driver", function(doc) {
                	return {
                                filters: {
                                        'status': 'Active', 
                                        'employment_type': 'Commission' 
				}
                        };
		});
		if ((cur_frm.doc.docstatus != 1) && (!cur_frm.doc.__islocal))
			frm.events.driver(frm);
	}
});

// Copyright (c) 2018, Bilal Ghayad and contributors
// For license information, please see license.txt

cur_frm.add_fetch('driver', 'employee_name', 'driver_name')
cur_frm.add_fetch('driver', 'employment_type', 'employment_type')
cur_frm.add_fetch('driver', 'money_collection_account', 'driver_cash_account')

frappe.ui.form.on('Clearance With Driver', {
	refresh: function(frm) {

	},
        onload: function(frm) {
                frm.set_query("driver", function(doc) {
                        return {
                                filters: {
                                        'status': 'Active'
                                }
                        };
                });

                frm.set_query("receiving_payment_account", function(doc) {
                        return {
                                filters: {
                                        'root_type': 'Asset',
                                        'company': frm.doc.company
                                }
                        };
                });

                frm.set_query("account_paid_from", function(doc) {
                        return {
                                filters: {
                                        'root_type': 'Asset',
                                        'company': frm.doc.company
                                }
                        };
                });

                frm.set_query("expenses_account", function(doc) {
                        return {
                                filters: {
                                        'root_type': 'Expense',
                                        'company': frm.doc.company
                                }
                        };
                });

        },
	driver: function(frm) {
		if (cur_frm.doc.driver) {
			ClearVariables(frm);
//			cur_frm.reset();
//			var SelectedDriver = cur_frm.doc.driver;
			GetClrVehStrt(frm);
			get_values(frm);
//			cur_frm.doc.reset();
//			document.getElementById(cur_frm).reset();
//			this.frm.reset();
//			cur_frm.reset();
//			cur_frm.document.forms[cur_frm].reset();
		}
	},

	get_data: function(frm) {
		get_values(frm);
	}
});


var GetClrVehStrt = function(frm) {

//	var SelectedDriver = cur_frm.doc.driver;
//	if (!cur_frm.doc.clearance_date) {
//		var d = new Date().toLocaleString({ hour12: false });
//		frappe.msgprint(__("Welcome: {0}", [d]));
//		cur_frm.set_value("clearance_date", d);
//		refresh_field("clearance_date");
//	}
	frappe.call({
//      	method: "taxi.taxi.doctype.trip_order.trip_order.get_vehicle",
                method: "taxi.taxi.doctype.clearance_with_driver.clearance_with_driver.GetClrVehStrt",
                args: {
                	"driver": frm.doc.driver,
               		"clearance_date": frm.doc.clearance_date
                },
                callback: function(r) {
//			frappe.msgprint(__("In Javascript Cash with him is: {0}", [r.message[3]]));
			if (!frm.doc.clearance_date) {
                                cur_frm.set_value("clearance_date", r.message[5]);
//				frm.doc.clearance_date = r.message[5];
				refresh_field("clearance_date");
			}
//			frappe.msgprint(__("Welcome: {0}", [r.message[2]]));
                	if (r.message) {

//				frappe.msgprint(__("In Javascript Cash with him is: {0}", [r.message[3]]));
                                cur_frm.set_value("cash_with_him", r.message[4]);
				var lastpayment = r.message[1];
				if (lastpayment[0]) {
					frappe.msgprint(__("Last Payment Date: {0}", [r.message[1][0]['modified']]));
                                	cur_frm.set_value("last_payment_date", r.message[1][0]['modified']);
				}
				else			
                                	cur_frm.set_value("last_payment_date", "");
//				refresh_field("cash_with_him");
				var last_clr = r.message[2];
//				frappe.msgprint(__("Last Clearance: {0}", [r.message[2][0]['modified']]));
				if (r.message[0]) {
                                	cur_frm.set_value("vehicle", r.message[0]);
				}
				else {						
                                	cur_frm.set_value("vehicle", "Please Select Vehicle");
				}
//				if (r.message[1][0]['modified'] == "") {
				if (last_clr[0]) {
					cur_frm.set_value("last_clearance_date", r.message[2][0]['modified']);
					cur_frm.set_value("join_date", "");
				}
				else {
					cur_frm.set_value("join_date", r.message[3]);
					cur_frm.set_value("last_clearance_date", "");
				}
                        }
                }
        })
}


var get_values = function(frm) {
	if (frm.doc.clearance_date) {
		frappe.call({
        		method: "taxi.taxi.doctype.clearance_with_driver.clearance_with_driver.get_values",
                	args: {
                		"driver": frm.doc.driver,
                		"clearance_date": frm.doc.clearance_date
                	},
                	callback: function(r) {
                		if (r.message) {
//					frappe.msgprint(__("Welcome Not Commission: {0}", [r.message[5][0]['total_maint']]));
					var statement = r.message[4];
//					var last_payment = r.message[2];
//					var last_clearance = r.message[3];
//					if (last_clearance == "")
//                              		cur_frm.set_value("join_date", r.message[10]);
//					else
//                              		cur_frm.set_value("last_clearance_date", last_clearance[0]['modified']);
//	                        	cur_frm.set_value("cash_with_him", r.message[1]);
//                                	cur_frm.set_value("last_payment_date", last_payment[0]['creation']);
					filling_and_calculation(frm, statement);
//					frappe.msgprint(__("Welcome Not Commission: {0}", [r.message[5][0]['total_maint']]));
					if (cur_frm.doc.employment_type != "Commission") {	
//					frappe.msgprint(__("Welcome Not Commission: {0}", [r.message[5][0]['total_maint']]));
	                        		cur_frm.set_value("maintenance_amount", r.message[5][0]['total_maint']);
	                               		cur_frm.set_value("amount_due_to_us", r.message[1]);
	                               		cur_frm.set_value("amount_due_to_driver", 0);
	                               		cur_frm.set_value("driver_commission_amount", 0);
	                               		cur_frm.set_value("no_of_driver_due_weekly_fees", 0);
	                               		cur_frm.set_value("driver_due_weekly_fees", 0);
	                               		cur_frm.set_value("amount_due_to_driver_cal", 0);
					}
	                               		cur_frm.set_value("collected_money_out_of_orders", r.message[8][0]['total_col_mon_out']);
	                               		cur_frm.set_value("delivered_payments_to_office", r.message[9][0]['total_delivered_mon']);
	                               		cur_frm.set_value("net_cash", flt(cur_frm.doc.total_cash_orders_amount) + flt(cur_frm.doc.collected_money_within_orders) + flt(cur_frm.doc.collected_money_out_of_orders) - flt(cur_frm.doc.delivered_payments_to_office) - flt(cur_frm.doc.maintenance_amount));
	                               		cur_frm.set_value("driver_cash_account_balance", r.message[1]);
	                               		cur_frm.set_value("amount_due_to_us_cal", flt(r.message[1]) - flt(cur_frm.doc.amount_due_to_driver_cal));
                        	}
                	}
        	})
		refresh_field("statement_of_trips_orders");
	}
}
	
var filling_and_calculation = function(frm, statement) {
//	frappe.msgprint(__("Welcome: {0}", [statement[0]['creation']]));
//	frappe.msgprint(__("Welcome Not Commission: {0}"));
	cur_frm.clear_table("statement_of_trips_orders");
	var new_row;
	var total_orders_amount = 0.00;
	var total_cash_orders_amount = 0.00;
	var total_credit_orders_amount = 0.00;
	var collected_money_within_orders = 0.00;
//	frappe.msgprint(__("Welcome Not Commission: {0}"));
	$.each(statement, function(i, row) {
//		frappe.msgprint(__("Welcome: {0}", [row.name]));
		new_row = frappe.model.add_child(cur_frm.doc, "Driver Clearance Trips Orders", "statement_of_trips_orders");
		new_row.trip_order = row.name;
		new_row.desc = row.title;
		new_row.date = row.creation;
		new_row.amount = row.grand_total;
		new_row.cash = row.cash_amount;
		new_row.credit = row.credit_amount;
		new_row.money_collection = row.money_collection;
		new_row.clearance_status = row.driver_clearance_status;
		total_orders_amount = total_orders_amount + flt(row.grand_total);
		total_cash_orders_amount = total_cash_orders_amount + flt(row.cash_amount);
		total_credit_orders_amount = total_credit_orders_amount + flt(row.credit_amount);
		collected_money_within_orders = collected_money_within_orders + flt(row.money_collection);
	});
//	frappe.msgprint(__("Welcome Not Commission: {0}"));
	refresh_field("statement_of_trips_orders");
	cur_frm.set_value("total_orders_amount", total_orders_amount); 
	cur_frm.set_value("total_cash_orders_amount", total_cash_orders_amount); 
	cur_frm.set_value("total_credit_orders_amount", total_credit_orders_amount);
	cur_frm.set_value("collected_money_within_orders", collected_money_within_orders);
//	frappe.msgprint(__("Welcome Not Commission: {0}"));
//	frappe.msgprint(__("Welcome Not Commission: {0}", [collected_money_within_orders]));
//	frappe.msgprint(__("Welcome Not Commission: {0}", [r.message[5][0]['total_maint']]));
	var child_table_length = frm.doc.statement_of_trips_orders.length;
//	frappe.msgprint(__("Welcome child_table_length: {0}", [child_table_length]));
	if (child_table_length > 0) {
		var duration_in_hour = frappe.datetime.get_hour_diff(frm.doc.statement_of_trips_orders[0]["date"], frm.doc.statement_of_trips_orders[child_table_length - 1]["date"]);
		var duration_in_day = duration_in_hour / 24;

		frappe.msgprint(__("Welcome Duration in Day: {0}", [duration_in_day]));
		cur_frm.set_value("duration_clearance", duration_in_day);
	}
	else {	
		cur_frm.set_value("duration_clearance", 0);
		frappe.msgprint(__("Welcome Duration in Day: {0}", 0));
	}

//	frappe.msgprint(__("Welcome Not Commission: {0}", [duration_in_day]));
//	cur_frm.set_value("duration_clearance", frappe.datetime.get_day_diff(frm.doc.statement_of_trips_orders[0]["date"], frm.doc.statement_of_trips_orders[child_table_length - 1]["date"]));

}


var ClearVariables = function(frm) {

	frm.set_value('amount_due_to_us', "");
	frm.set_value('amount_due_to_driver', "");
	frm.clear_table("statement_of_trips_orders");
        refresh_field("statement_of_trips_orders");
	frm.set_value('total_orders_amount', "");
	frm.set_value('total_cash_orders_amount', "");
	frm.set_value('total_credit_orders_amount', "");
	frm.set_value('collected_money_within_orders', "");
	frm.set_value('maintenance_amount', "");
	frm.set_value('collected_money_out_of_orders', "");
	frm.set_value('delivered_payments_to_office', "");
	frm.set_value('net_cash', "");
	frm.set_value('driver_commission_amount', "");
	frm.set_value('no_of_driver_due_weekly_fees', "");
	frm.set_value('driver_due_weekly_fees', "");
	frm.set_value('amount_due_to_driver_cal', "");
//	frm.set_value('driver_cash_account', "");
	frm.set_value('driver_cash_account_balance', "");
	frm.set_value('amount_due_to_us_cal', "");
	frm.set_value('duration_clearance', "");
	frm.set_value('paid_amount_1', "");
	frm.set_value('from_account_1', "");
	frm.set_value('from_account_1_balance_before', "");
	frm.set_value('from_account_1_balance_after', "");
	frm.set_value('payment_1_description', "");
	frm.set_value('to_account_1', "");
	frm.set_value('to_account_1_balance_before', "");
	frm.set_value('to_account_1_balance_after', "");
	frm.set_value('paid_amount_2', "");
	frm.set_value('from_account_2', "");
	frm.set_value('from_account_2_balance_before', "");
	frm.set_value('from_account_2_balance_after', "");
	frm.set_value('payment_2_description', "");
	frm.set_value('to_account_2', "");
	frm.set_value('to_account_2_balance_before', "");
	frm.set_value('to_account_2_balance_after', "");
	frm.set_value('receiving_payment_account', "");
	frm.set_value('account_paid_from', "");
	frm.set_value('expenses_account', "");
}

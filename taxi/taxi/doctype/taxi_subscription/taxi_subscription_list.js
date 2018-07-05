frappe.listview_settings['Taxi Subscription'] = {
        add_fields: ["grand_total", "outstanding_amount", "active", "end_date"],
        get_indicator: function(doc) {
                if(flt(doc.outstanding_amount)===0) {
			if (doc.active == 'Yes') {
				if (doc.end_date >= frappe.datetime.nowdate()) {
					return [__("Paid-Active-Valid"), "green", "outstanding_amount,=,0|end_date,>=,Today|active,=,Yes"];
				}
				else {
					return [__("Paid-Active-Expired"), "blue", "outstanding_amount,=,0|end_date,<,Today|active,=,Yes"];
				}
			}
			else if (doc.end_date >= frappe.datetime.nowdate()){
                        	return [__("Paid-NotActive-Valid"), "red", "outstanding_amount,=,0|end_date,>=,Today|active,=,No"];
			}
			else {
				return [__("Paid-NotActive-Expired"), "orange", "outstanding_amount,>,0|end_date,<,Today|active,=,No"];
			}

                } else if (flt(doc.outstanding_amount) > 0) {
			if (doc.active == 'Yes') {
				if (doc.end_date >= frappe.datetime.nowdate()) {
					return [__("Unpaid-Active-Valid"), "red", "outstanding_amount,>,0"];
				}
				else {
					return [__("UnPaid-Active-Expired"), "red", "outstanding_amount,>,0"];
				}
			}
			else if (doc.end_date >= frappe.datetime.nowdate()) {
				return [__("Unpaid-NotActive-Valid"), "orange", "outstanding_amount,>,0"];
			}
			else {
				return [__("Unpaid-NotActive-Expired"), "blue", "outstanding_amount,>,0"];
			}
                }
	}
};

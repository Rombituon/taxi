frappe.listview_settings['Trip Order'] = {
        add_fields: ["grand_total", "outstanding_amount"],
        get_indicator: function(doc) {
                if(flt(doc.outstanding_amount)===0) {
                        return [__("Paid"), "green", "outstanding_amount,=,0"];
                } else if (flt(doc.outstanding_amount) > 0) {
                        return [__("Unpaid"), "orange", "outstanding_amount,>,0"];
                }
	}
};

//frappe.listview_settings['Trip Order'] = {
//        add_fields: ["order_status"],
//        get_indicator: function(doc) {
//		return [__(doc.order_status), {
//			"In Progress": "blue",
//			"Assigned": "orange",
//			"Scheduled": "orange",
//			"Done": "blue",
//			"Cancelled": "red",
//		}[doc.order_status], "order_status,=," + doc.order_status];
//	}
//};
//               if(doc.order_status === "Done") {
//                        return [__(doc.order_status), "green", "order_status,=," + doc.order_status];
//                } else if (doc.order_status ===  "Assigned") {
//                        return [__(doc.order_status), "orange", "order_status,=," + doc.order_status];
//                }
//        }
//};

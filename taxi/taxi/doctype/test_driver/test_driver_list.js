// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings['Test Driver'] = {
        add_fields: ["name", "address"],
        get_indicator: function(doc) {
                if(doc.enable==1) {
                        return [__("Enabled"), "blue", "enable,=,1"];
                } else if(flt(doc.outstanding_amount)==0) {
//                      return [__("KoKo"), "green", "outstanding_amount,=,0"]
                        return [__("Not Enabled"), "orange", "enable,=,0"]
                } 

        },
        right_column: "address"
};

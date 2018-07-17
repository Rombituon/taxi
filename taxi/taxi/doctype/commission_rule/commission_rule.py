# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bilal Ghayad and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document, _

class CommissionRule(Document):
#	pass
        def validate(self):
                any_commission_rule = frappe.db.sql("""
                select * from `tabCommission Rule` where commission_percent = %s and weekly_fees = %s and name != %s and docstatus != 2""", (self.commission_percent, self.weekly_fees, self.name))
		if len(any_commission_rule) > 0:
			frappe.throw(_("There is a rule same as this rule, sorry can not save it")) 
                else:
			self.title = str(self.commission_percent) + "%" + "-" + str(self.weekly_fees) + "LBP"


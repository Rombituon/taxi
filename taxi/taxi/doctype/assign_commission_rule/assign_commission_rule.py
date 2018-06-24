# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bilal Ghayad and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document, _
from datetime import datetime
from datetime import timedelta



class AssignCommissionRule(Document):
#	pass
        def validate(self):
                self.title = self.driver_name
		if not self.active_date:
			frappe.throw(_("Active Date need to be filled"))
		elif not self.commission_rule:
			frappe.throw(_("Commission Rule need to be filled"))
		elif self.active_date <= self.last_clearance_date:
			frappe.throw(_("The active date need to be after last clearance date"))

                Last_ACR = frappe.db.sql("""
                        select name from `tabAssign Commission Rule`
                        where driver = %s and docstatus = 1 and name != %s order by modified desc limit 1
                        """,(self.driver, self.name), as_dict=True)

                Last_ACR_CLR = frappe.db.sql("""
                        select name from `tabClearance With Driver`
                        where assign_com_rule = (select name from `tabAssign Commission Rule`
                        where driver = %s and docstatus = 1 and name != %s order by modified desc limit 1)
                        """, (self.driver, self.name), as_dict=True)

                if (len(Last_ACR_CLR) == 0 and len(Last_ACR) > 0):

                        frappe.throw(_("The Assign Commission Rule {0} is submitted and not used with \
                        any clearance, please modify it or do clearance first."). format(Last_ACR[0]['name']))


#		self.check_driver_acrl()

#	def onload(self):

#		if ((self.docstatus != 1) and (self.docstatus != 0)):
#		if self.docstatus != 1:
#			self.update_data()

#			LatestEntriesDates = get_values(self.driver)
#			self.last_clearance = LatestEntriesDates[0][0]['name']
#			self.last_clearance_date = LatestEntriesDates[0][0]['clearance_date']
			
#			self.last_assigned_commission_rule = LatestEntriesDates[1][0]['name']
#			self.last_acr_active_date = LatestEntriesDates[1][0]['active_date']
#			self.active_date = self.last_clearance_date + timedelta(minutes=1)
#			self.save(ignore_permissions = True)
#			frappe.db.commit()

#     			frappe.msgprint(_("Last clearance is {0} and last date is {1}"). format(LatestEntriesDates[0][0]['name'], LatestEntriesDates[0][0]['clearance_date']))
#     			frappe.msgprint(_("Last ACR is {0} and last active date is {1}"). format(LatestEntriesDates[1][0]['name'], LatestEntriesDates[1][0]['active_date']))
#     			frappe.msgprint(_("Active Date is {0}"). format(self.active_date))
#			self.save()
#	def update_data(self):
#		LatestEntriesDates = get_values(self.driver)
#		self.last_clearance = LatestEntriesDates[0][0]['name']
#		self.last_clearance_date = LatestEntriesDates[0][0]['clearance_date']
#		self.last_assigned_commission_rule = LatestEntriesDates[1][0]['name']
#		self.last_acr_active_date = LatestEntriesDates[1][0]['active_date']
#		self.active_date = self.last_clearance_date + timedelta(minutes=1)
#               self.save(ignore_permissions = True)
#               frappe.db.commit()

#                frappe.msgprint(_("Last clearance is {0} and last date is {1}"). format(LatestEntriesDates[0][0]['name'], LatestEntriesDates[0][0]['clearance_date']))
#                frappe.msgprint(_("Last ACR is {0} and last active date is {1}"). format(LatestEntriesDates[1][0]['name'], LatestEntriesDates[1][0]['active_date']))
#                frappe.msgprint(_("Active Date is {0}"). format(self.active_date))
#		self.save()



	def check_driver_acrl(self):

                AnyACRL = frappe.db.sql("""
                select * from `tabAssign Commission Rule` where driver = %s and name != %s and docstatus != 2""", (self.driver, self.name), as_dict=True)
		
#     		frappe.msgprint(_("The AnyACRL is: {0}"). format(AnyACRL[0]['name']))
		
		if len(AnyACRL) > 0:
                        frappe.throw(_("There is {0} saved and not submmited for this driver, please complete and submit it"). format(AnyACRL[0]['name']))
		
#                else:
#                        self.title = str(self.commission_percent) + "%" + "-" + str(self.weekly_fees) + "LBP"
		
        def on_submit(self):

		Last_ACR = frappe.db.sql("""
			select name from `tabAssign Commission Rule`
                        where driver = %s and docstatus = 1 and name != %s order by modified desc limit 1
			""",(self.driver, self.name), as_dict=True)

		Last_ACR_CLR = frappe.db.sql("""
			select name from `tabClearance With Driver` 
			where assign_com_rule = (select name from `tabAssign Commission Rule` 
			where driver = %s and docstatus = 1 and name != %s order by modified desc limit 1)
			""", (self.driver, self.name), as_dict=True)

		if (len(Last_ACR_CLR) == 0 and len(Last_ACR) > 0):
			
                        frappe.throw(_("The Assign Commission Rule {0} is submitted and not used with \
			any clearance, please modify it or do clearance first."). format(Last_ACR[0]['name']))


@frappe.whitelist()
def get_values(AssignedDriver):

	LastClearance = frappe.db.sql("""select name, clearance_date from `tabClearance With Driver` 
			where docstatus = 0 and driver = %(driver_id)s order by clearance_date desc limit 3
			""", {"driver_id": AssignedDriver}, as_dict=True)

	LastAssigned = frappe.db.sql("""select name, active_date, commission_rule, commission_percent, weekly_fees from `tabAssign Commission Rule` 
			where docstatus = 1 and driver = %(driver_id)s order by active_date desc limit 1
			""", {"driver_id": AssignedDriver}, as_dict=True)

	FirstTO = frappe.db.sql("""select assigned_driver, modified from `tabTrip Order`
                        where docstatus = 1 and assigned_driver = %(driver_id)s order by modified asc limit 1
                        """, {"driver_id": AssignedDriver}, as_dict=True)

	HiringDate = frappe.db.get_value('Employee', {"name": AssignedDriver} ,'date_of_joining')

#       self.hop_no_discounted  = frappe.db.get_value("Route Pricing Settings", "hop_no_discounted")


#	frappe.msgprint(_("Number of rows of Last Clearance is: {0}"). format(len(LastClearance)))

	return LastClearance, LastAssigned, FirstTO, HiringDate

# -*- coding: utf-8 -*-
# Copyright (c) 2017, Bilal Ghayad and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
from frappe import _, scrub, ValidationError, msgprint
from frappe.model.document import Document, _
from frappe import utils
import datetime
from frappe.utils import flt, comma_or, nowdate
from erpnext.accounts.utils import get_outstanding_invoices, get_account_currency, get_balance_on
from erpnext.accounts.party import get_party_account
#from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from erpnext.accounts.doctype.journal_entry.journal_entry \
        import get_average_exchange_rate, get_default_bank_cash_account
from erpnext.setup.utils import get_exchange_rate
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.accounts.general_ledger import delete_gl_entries
from erpnext.controllers.selling_controller import SellingController
from erpnext.controllers.accounts_controller import AccountsController
#import Tkinter
#import tkMessageBox
#import Tkinter as tk
#import tkMessageBox
#from frappe.custom.doctype.property_setter.property_setter import make_property_setter

#class TripOrder(Document):
#class TripOrder(SellingController):
class TripOrder(AccountsController):

#	pass
	def validate(self):

		self.last_note_time = frappe.db.get_value('Trip Order', {'name': self.name}, 'last_note_time')
		self.notified = frappe.db.get_value('Trip Order', {'name': self.name}, 'notified')
		if not (self.customer):
			self.title = self.origination_place + "-" + self.final_destination
		else:
			self.title = self.customer + "-" + self.origination_place + "-" + self.final_destination
		if (self.credit_amount > 0 and self.money_collection > 0):
			frappe.throw(_("Can not set money collection amount > 0 if credit amount > 0, please correct"))

		self.outstanding_amount = self.credit_amount

                self.posting_date = self.transaction_date
                self.due_date = self.posting_date


	def on_cancel(self):

		delete_gl_entries(voucher_type=self.doctype, voucher_no=self.name)



        def on_submit(self):
		
#		if self.cash_amount > 0:
#			if self.order_status != "Done":
#				frappe.throw(_("Order Status must be Done to be able to submit the order"))		
		if (self.order_status != "Done" and self.order_status != "Cancelled" and self.order_status != "In Progress"):
				frappe.throw(_("As cash amount is zero, Order Status must be Cancelled or Done to be able to submit the order"))
		elif not frappe.db.get_value('Employee', {'name': self.assigned_driver}, 'money_collection_account'):
				frappe.throw(_("Money Collection Account need to be set for Employee"))


		self.outstanding_amount = self.credit_amount
                self.posting_date = self.transaction_date
                self.make_gl_entries()


	def make_gl_entries(self):

		customer_gl_entries =  self.get_gl_dict({
			"account": self.receivable_account,
			"party_type": "Customer",
			"party": self.customer,
			"against": self.income_account,
			"debit": self.grand_total,
			"debit_in_account_currency": self.grand_total,
			"against_voucher": self.name,
			"against_voucher_type": self.doctype
                })

		trip_gl_entry = self.get_gl_dict({
			"account": self.income_account,
			"against": self.customer,
			"credit": self.grand_total,
			"credit_in_account_currency": self.grand_total,
			"cost_center": self.cost_center
		})

		make_gl_entries([customer_gl_entries, trip_gl_entry], cancel=(self.docstatus == 2),
			update_outstanding="Yes", merge_entries=False)


		if self.cash_amount > 0:

			customer_gl_entries =  self.get_gl_dict({
				"account": self.receivable_account,
				"party_type": "Customer",
				"party": self.customer,
				"against": self.driver_cash_account,
				"credit": self.cash_amount,
				"credit_in_account_currency": self.cash_amount,
				"against_voucher": self.name,
				"against_voucher_type": self.doctype
			})

			paid_to_gl_entry = self.get_gl_dict({
				"account": self.driver_cash_account,
				"against": self.customer,
				"debit": self.cash_amount,
				"debit_in_account_currency": self.cash_amount,
				"cost_center": self.cost_center
			})


			make_gl_entries([customer_gl_entries, paid_to_gl_entry], cancel=(self.docstatus == 2),
				update_outstanding="Yes", merge_entries=False)

		if self.money_collection > 0:

			customer_gl_entries =  self.get_gl_dict({
				"account": self.receivable_account,
				"party_type": "Customer",
				"party": self.customer,
				"against": self.driver_cash_account,
				"credit": self.money_collection,
				"credit_in_account_currency": self.money_collection,
				"against_voucher": self.name,
				"against_voucher_type": self.doctype
                	})

			paid_to_gl_entry = self.get_gl_dict({
                        	"account": self.driver_cash_account,
                        	"against": self.customer,
                        	"debit": self.money_collection,
                        	"debit_in_account_currency": self.money_collection,
                        	"cost_center": self.cost_center
                	})

			make_gl_entries([customer_gl_entries, paid_to_gl_entry], cancel=(self.docstatus == 2),
				update_outstanding="Yes", merge_entries=False)

@frappe.whitelist()
def get_settings():

	DiscountedHopNo  = frappe.db.get_single_value('Route Pricing Settings', 'hop_no_discounted')
	HopNoToReturnForNormalRating  = frappe.db.get_single_value('Route Pricing Settings', 'return_to_normal_rating_hop_no')
	PriceForSecondHop  = frappe.db.get_single_value('Route Pricing Settings', 'second_hop_price')

	return DiscountedHopNo, HopNoToReturnForNormalRating, PriceForSecondHop


@frappe.whitelist()
def get_vehicle(AssignedDriver):
	assigned_vehicle = frappe.db.get_value('Vehicle', {'employee': AssignedDriver}, 'name')
	return assigned_vehicle


@frappe.whitelist()
def popup_notification():

	get_notification = frappe.db.sql("""select name, customer, delivery_time, popup_reminder, 
		notify_before, re_notify, last_note_time, notified, re_notify_every
		from `tabTrip Order` where 
		delivery_time is not null
		and order_status != 'Assigned And Notified'
		and popup_reminder = 1
		and month(delivery_time) = month(now())
		and year(delivery_time) = year(now())
		and docstatus = 0
		and (notified = 'No' or (notified = 'Yes' and re_notify = 1))
		""", as_dict=True)


	for d in get_notification:
		if d['notified'] == 'No':
			cur_time = datetime.datetime.now()
			if int (d['delivery_time'].day) == cur_time.day:
				time_diff = ((d['delivery_time'].hour - cur_time.hour) * 60 + (d['delivery_time'].minute - cur_time.minute))
#				if time_diff < int (d['notify_before']) and time_diff > -60:
				if time_diff < int (d['notify_before']):
					msg_var = "Notify Before Order (before 12 PM): Please follow up Trip Order # {0} as its delivery time is: {1} for customer: {2} and the time difference is {3} and notify before is {4} for user {5}".format(d['name'], d['delivery_time'], d['customer'], time_diff, d['notify_before'], frappe.session.user)
#			test_msg = "The popup reminder case is {0}".format(d['popup_reminder'])
					frappe.publish_realtime(event='msgprint', message=msg_var, user=frappe.session.user)

					to_note_count = frappe.db.sql("""update `tabTrip Order` 
						set last_note_time = %s, notified = 'Yes'
						where name = %s
						""", (cur_time, d['name']), as_dict=True)

					frappe.db.commit()

#					frappe.db.set_value("Trip Order", d['name'], "last_note_time", cur_time)
#					frappe.db.set_value("Trip Order", d['name'], "notified", 'Yes')
#					frappe.publish_realtime(event='eval_js', message='refresh_field("last_note_time")')

			elif int(d['delivery_time'].day) == (cur_time.day - 1):
#				if  (int(d['delivery_time'].hour) - cur_time.hour) == 23:
#				if  (int(d['delivery_time'].hour) - 0) == 23:

#					time_diff = (cur_time.hour + 24 - d['delivery_time'].hour) * 60 + (cur_time.minute - d['delivery_time'].minute)
#					time_diff = (d['delivery_time'].minute - cur_time.minute)
#					if time_diff <= 120 and time_diff >= 0:
				msg_var = "Notify Before Order (after 12 PM): Please follow up Trip Order # {0} as its delivery time is: {1} for customer: {2} and notify before is {3}".format(d['name'], d['delivery_time'], d['customer'], d['notify_before'])
				frappe.publish_realtime(event='msgprint', message=msg_var, user=frappe.session.user)

				to_note_count = frappe.db.sql("""update `tabTrip Order` 
					set last_note_time = %s, notified = 'Yes'
					where name = %s
					""", (cur_time, d['name']), as_dict=True)

				frappe.db.commit()

			elif int(d['delivery_time'].day) == (cur_time.day + 1):

				time_diff = (24 - cur_time.hour + d['last_note_time'].hour) * 60 + (cur_time.minute - d['last_note_time'].minute)
#				time_diff = 60 - cur_time.minute + d['delivery_time'].minute
#				if time_diff < int (d['notify_before']) and time_diff > -60:
				if time_diff < int (d['notify_before']):
				
					msg_var = "Notify Before Order (Order after 12 PM): Please follow up Trip Order # {0} as its delivery time is: {1} for customer: {2} and notify before is {3}".format(d['name'], d['delivery_time'], d['customer'], d['notify_before'])
					frappe.publish_realtime(event='msgprint', message=msg_var, user=frappe.session.user)

					to_note_count = frappe.db.sql("""update `tabTrip Order` 
						set last_note_time = %s, notified = 'Yes'
						where name = %s
						""", (cur_time, d['name']), as_dict=True)

					frappe.db.commit()


#				frappe.db.set_value("Trip Order", d['name'], "last_note_time", cur_time)
#				frappe.db.set_value("Trip Order", d['name'], "notified", 'Yes')
#				frappe.publish_realtime(event='eval_js', message='cur_frm.set_value("last_note_time", {0}'.cur_time)
		else:
			cur_time = datetime.datetime.now()
			if int(d['last_note_time'].day) == cur_time.day:
				time_diff = (cur_time.hour - d['last_note_time'].hour) * 60 + (cur_time.minute - d['last_note_time'].minute)
				if time_diff > int (d['re_notify_every']):
#					doc = frappe.get_doc("Trip Order", d['name'])
#					doc.last_note_time = cur_time
					msg_var = "Reminder (Before 12 PM): Please follow up Trip Order # {0} as its delivery time is: {1} for customer: {2} and the time difference is {3} and notify before is {4}".format(d['name'], d['delivery_time'], d['customer'], time_diff, d['notify_before'])
					frappe.publish_realtime(event='msgprint', message=msg_var, user=frappe.session.user)

					to_note_count = frappe.db.sql("""update `tabTrip Order` 
						set last_note_time = %s, notified = 'Yes'
						where name = %s
						""", (cur_time, d['name']), as_dict=True)

					frappe.db.commit()
#					frappe.publish_realtime(event='eval_js', message='cur_frm.set_value("last_note_time", {0})'.format(cur_time), user=frappe.session.user)
#					frappe.publish_realtime(event='eval_js', message='refresh_field("last_note_time")', user=frappe.session.user)
#					frappe.db.set_value("Trip Order", d['name'], "last_note_time", cur_time)
#					frappe.publish_realtime(event='eval_js', message='refresh_field("last_note_time")')
			elif int(d['last_note_time'].day) == (cur_time.day - 1):
				time_diff = (cur_time.hour + 24 - d['last_note_time'].hour) * 60 + (cur_time.minute - d['last_note_time'].minute)
				if time_diff > int (d['re_notify_every']):

					msg_var = "Reminder (After 12 PM): Please follow up Trip Order # {0} as its delivery time is: {1} for customer: {2} and the time difference is {3} and notify before is {4}".format(d['name'], d['delivery_time'], d['customer'], time_diff, d['notify_before'])

					frappe.publish_realtime(event='msgprint', message=msg_var, user=frappe.session.user)

					to_note_count = frappe.db.sql("""update `tabTrip Order` 
						set last_note_time = %s, notified = 'Yes'
						where name = %s
						""", (cur_time, d['name']), as_dict=True)

					frappe.db.commit()
#					frappe.publish_realtime(event='eval_js', message='frm.set_value("last_note_time", {0})'.format(cur_time), user=frappe.session.user)
#					frappe.publish_realtime(event='eval_js', message='refresh_field("last_note_time")', user=frappe.session.user)
#					frappe.db.set_value("Trip Order", d['name'], "last_note_time", cur_time)
#					frappe.publish_realtime(event='eval_js', message='refresh_field("last_note_time")')
#		if d.notified == "Yes":
#			if d.re_notify == 1:
#				cur_time = datetime.datetime.now()
#				cur_time.hour - d.last_note_time.hour
#				d.last_note_time
#		test_msg = "This is delivery time: {0} and the hour is {1}".format(d['delivery_time'], d['delivery_time'].hour)
#		test_msg = "This is delivery time"
#		frappe.publish_realtime(event='msgprint', message=test_msg, user=frappe.session.user)

	cur_time = datetime.datetime.now()

	msg_var = "The returned values are {0}, {1}, {2}, {3} and current time is {4} and current hour is {5} and current minute is {6}".format(get_notification[0]['name'], get_notification[0]['customer'], get_notification[0]['delivery_time'], get_notification[0]['popup_reminder'], cur_time, cur_time.hour, cur_time.minute)


#	frappe.publish_realtime(event='eval_js', message='show_alert("Show Alert: {0}")'.format(msg_var), user=frappe.session.user)
	frappe.publish_realtime(event='eval_js', message='show_alert("Show Alert for 30 sec {0}", 30)'.format(msg_var), user=frappe.session.user)

	return

#	return frappe.publish_realtime(event='msgprint', message=msg_var, user=frappe.session.user)
#	return frappe.publish_realtime(event='eval_js', message='alert("Second Alert {0} and {1}")'.format(msg_var, msg_var), user=frappe.session.user)
#	return frappe.publish_realtime('display_notification', msg_var, user=frappe.session.user)

#	return frappe.msgprint("The returned queries are: {0}, {1}, {2}, {3}". format(get_notification[0]['name'], get_notification[0]['customer'], get_notification[0]['delivery_time'], get_notification[0]['popup_reminder']))






#	return frappe.publish_realtime(event='show_alert', message='Test ya habibi', user=frappe.session.user, after_commit=True)

#	get_notification = frappe.db.sql("""select name, customer, delivery_time, popup_reminder, notify_before, 
#		hour(delivery_time) as hr_deliv, minute(delivery_time) as m_deliv
#		from `tabTrip Order` where delivery_time is not null
#		where name in (select trip_order from `tabDriver Clearance Trips Orders` where parent = %s)
#		""", (self.name), as_dict=True)


#	import matplotlib
#	matplotlib.use('tkagg')
#	import matplotlib.pyplot as plt
#	plt.plot([1, 2, 3])
#	return plt.show()
#	app = Tkinter.Tk()
#	choice = tkMessageBox.askquestion("Yes/No", "Are you sure?", icon='warning')
#	return app.mainloop()
#	window = tk.Tk()
#	window.wm_withdraw()
#	return tkMessageBox.showinfo(title="Greetings", message="Hello World!")

#	return tkMessageBox.showinfo(title="Information", message="Created in Python.")
#	return frappe.publish_realtime(event='msgprint', message='Test ya habibi', user=frappe.session.user, after_commit=True)
#	return frappe.publish_realtime(event='msgprint', message='Test ya habibi', user=frappe.session.user, after_commit=True)
#	return frappe.publish_realtime(event='confirm', message='Test ya habibi', user=frappe.session.user, after_commit=True)
#	return frappe.publish_realtime(event='show_alert', message='Test ya habibi', user=frappe.session.user, after_commit=True)
#	return frappe.publish_realtime(event='confirm', message='Test ya habibi', after_commit=True)


#	return frappe.db.set_value("Trip Order","TO-00003", "test_barcode", 77889900)
#	return frappe.msgprint(_("This Msg Print for Test"))

@frappe.whitelist()
def get_origination(doctype, txt, searchfield, start, page_len, filters):

	return frappe.db.sql("""Select item_code from `tabItem` where item_group = %s order by item_code desc""", (filters.get("itemgroup")))



@frappe.whitelist()
def get_customer_profile(date, party_type, party):

        get_subscription = frappe.db.sql("""select name from `tabTaxi Subscription` where customer = %s and active = 'Yes'
		and end_date >= CURDATE()
                and docstatus = 1
                """, (party), as_dict=True)
	cus_subscription = get_subscription[0]['name']

	if (len (get_subscription) > 0):

		subscribed = 'Yes'
		get_subsc_hops =  frappe.db.sql("""select idx, `from`, `to`, hop_price, parent as subsc_ref from `tabTaxi Subscription Hops` 
			where parent = %s 
			order by idx asc""", (get_subscription[0]['name']), as_dict=True)

#		get_subsc_hops[0]['Test'] = "Welcome"
#		get_subsc_hops[1]['Test'] = "New Welcome"

#		frappe.msgprint("The subscriber {0} is {1} Subscribed in subscription ref {2} and these are its hops {3} and {4}". format(party, subscribed, get_subscription, get_subsc_hops[0], get_subsc_hops[1]))

		i = 0
		for d in get_subsc_hops:
	
			get_subs_hops_info =  frappe.db.sql("""select parent as trip_order, docstatus, creation, `order`, trip_order_ref, hop_subsc_status from `tabTrip Order Subscriber Hops`
			where date(creation) = CURDATE() and `from` = %s and `to` = %s and subsc_ref = %s and docstatus != 2 
        	       	""", (d['from'], d['to'], d['subsc_ref']), as_dict=True)
			if (len(get_subs_hops_info) == 0):
				get_subsc_hops [i]['hop_subsc_status'] = "Available"
				get_subsc_hops [i]['trip_price'] = float (get_subsc_hops [i]['hop_price']) * 0.8

			elif (get_subs_hops_info[0]['order'] == "Buy" or get_subs_hops_info[0]['order'] == "Compensate" or get_subs_hops_info[0]['hop_subsc_status'] == "Taken"):
				get_subsc_hops [i]['hop_subsc_status'] = "Taken"

				if get_subs_hops_info[0]['hop_subsc_status'] == "Taken":
					get_subsc_hops [i]['trip_order_ref'] = get_subs_hops_info[0]['trip_order_ref']
				else:
					get_subsc_hops [i]['trip_order_ref'] = get_subs_hops_info[0]['trip_order']
				if get_subs_hops_info[0]['docstatus'] == 0:
					get_subsc_hops [i]['trip_order_status'] = "Draft"
				else:
					get_subsc_hops [i]['trip_order_status'] = "Submitted"
				get_subsc_hops [i]['trip_order_date'] = get_subs_hops_info[0]['creation']

			else:
				get_subsc_hops [i]['hop_subsc_status'] = "Available"
			i = i + 1 
	

#		frappe.msgprint("The subscriber {0} is {1} Subscribed in subscription ref {2} and these are its hops {3} and {4}". format(party, subscribed, get_subscription, get_subsc_hops[0], get_subsc_hops[1]))

	else:
		subscribed = 'No'
		cus_subscription = 'None'
	return cus_subscription, subscribed, get_subsc_hops


#	frappe.msgprint("At Python: The customer {0} has this subscription: {1}". format(party, get_subscription))


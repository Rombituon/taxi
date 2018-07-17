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
#class TaxiSubscription(Document):
#class TaxiSubscription(SellingController):
class TaxiSubscription(AccountsController):

#	pass
	def validate(self):

		self.last_note_time = frappe.db.get_value('TaxiSubscription', {'name': self.name}, 'last_note_time')
		self.notified = frappe.db.get_value('TaxiSubscription', {'name': self.name}, 'notified')
		if not (self.customer):
			self.title = format(self.no_rides_per_day) + " ride/day"
		else:
			self.title = self.customer + " -" + " " + format(self.no_rides_per_day) + " ride/day"

		self.outstanding_amount = self.credit_amount

                self.posting_date = self.transaction_date
                self.due_date = self.posting_date


	def on_cancel(self):

		delete_gl_entries(voucher_type=self.doctype, voucher_no=self.name)



        def on_submit(self):
		
		if (self.cash_amount > 0):
			if (self.cash_account is None):
				frappe.throw(_("Cash Account is required to be set"))

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

		subscription_gl_entry = self.get_gl_dict({
			"account": self.income_account,
			"against": self.customer,
			"credit": self.grand_total,
			"credit_in_account_currency": self.grand_total,
			"cost_center": self.cost_center
		})

		make_gl_entries([customer_gl_entries, subscription_gl_entry], cancel=(self.docstatus == 2),
			update_outstanding="Yes", merge_entries=False)


		if self.cash_amount > 0:

			customer_gl_entries =  self.get_gl_dict({
				"account": self.receivable_account,
				"party_type": "Customer",
				"party": self.customer,
				"against": self.cash_account,
				"credit": self.cash_amount,
				"credit_in_account_currency": self.cash_amount,
				"against_voucher": self.name,
				"against_voucher_type": self.doctype
			})

			paid_to_gl_entry = self.get_gl_dict({
				"account": self.cash_account,
				"against": self.customer,
				"debit": self.cash_amount,
				"debit_in_account_currency": self.cash_amount,
				"cost_center": self.cost_center
			})


			make_gl_entries([customer_gl_entries, paid_to_gl_entry], cancel=(self.docstatus == 2),
				update_outstanding="Yes", merge_entries=False)


@frappe.whitelist()
def get_settings():

	discounted_hop_no  = frappe.db.get_single_value('Route Pricing Settings', 'hop_no_discounted')
	hop_no_to_return_for_normal_rating  = frappe.db.get_single_value('Route Pricing Settings', 'return_to_normal_rating_hop_no')
	price_for_second_hop  = frappe.db.get_single_value('Route Pricing Settings', 'second_hop_price')

	return discounted_hop_no, hop_no_to_return_for_normal_rating, price_for_second_hop


@frappe.whitelist()
def get_vehicle(AssignedDriver):
	assigned_vehicle = frappe.db.get_value('Vehicle', {'employee': AssignedDriver}, 'name')
	return assigned_vehicle


@frappe.whitelist()
def get_origination(doctype, txt, searchfield, start, page_len, filters):

    return frappe.db.sql("""Select item_code from `tabItem` where item_group = %s order by item_code desc""", (filters.get("itemgroup")))

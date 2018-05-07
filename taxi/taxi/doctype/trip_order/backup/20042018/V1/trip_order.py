# -*- coding: utf-8 -*-
# Copyright (c) 2017, Bilal Ghayad and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
from frappe import _, scrub, ValidationError
from frappe.model.document import Document, _
from frappe.utils import flt, comma_or, nowdate
from erpnext.accounts.utils import get_outstanding_invoices, get_account_currency, get_balance_on
from erpnext.accounts.party import get_party_account
#from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from erpnext.accounts.doctype.journal_entry.journal_entry \
        import get_average_exchange_rate, get_default_bank_cash_account
from erpnext.setup.utils import get_exchange_rate
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.selling_controller import SellingController
from erpnext.controllers.accounts_controller import AccountsController
#from frappe.custom.doctype.property_setter.property_setter import make_property_setter

#class TripOrder(Document):
#class TripOrder(SellingController):
class TripOrder(AccountsController):

#	pass
	def validate(self):
		if not (self.customer):
			self.title = self.origination_place + "-" + self.final_destination
		else:
			self.title = self.customer + "-" + self.origination_place + "-" + self.final_destination
		if (self.credit_amount > 0 and self.money_collection > 0):
			frappe.throw(_("Can not set money collection amount > 0 if credit amount > 0, please correct"))

        def on_submit(self):
		
		if self.cash_amount > 0:
			if self.order_status != "Done":
				frappe.throw(_("Order Status must be Done to be able to submit the order"))		
		elif (self.order_status != "Done" and self.order_status != "Cancelled"):
				frappe.throw(_("As cash amount is zero, Order Status must be Cancelled or Done to be able to submit the order"))
		elif not frappe.db.get_value('Employee', {'name': self.assigned_driver}, 'money_collection_account'):
				frappe.throw(_("Money Collection Account need to be set for Employee"))


                self.posting_date = self.clearance_date
                self.make_gl_entries()


#		self.status = "Upaid"
#		self.set_status(update=True, status=self.status)
		sales_invoice_doc = make_sales_invoice("Trip Order", self.name)
#		sales_invoice_doc = make_sales_invoice("Trip Order", self.name)
	

		if sales_invoice_doc.status == "Unpaid":

			payment_entry_doc = make_payment_entry(sales_invoice_doc.name, self.name)
			frappe.msgprint(_("Sales Invoice {0} Submitted with status {1} and Payment Entry {2} Saved"). format(sales_invoice_doc.name, sales_invoice_doc.status, payment_entry_doc.name))
			self.status = sales_invoice_doc.status
		else:
			frappe.throw(_("Trip Order has not been submitted because of failing in sales invoice submitting"))


	def make_gl_entries(self):

		customer_gl_entries =  self.get_gl_dict({
			"account": self.receivable_account,
			"party_type": "Customer",
			"party": self.customer_name,
			"against": self.income_account,
			"debit": self.grand_total,
			"debit_in_account_currency": self.grand_total,
			"against_voucher": self.name,
			"against_voucher_type": self.doctype
                })

		trip_gl_entry = self.get_gl_dict({
			"account": self.income_account,
			"against": self.customer_name,
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
				"party": self.customer_name,
				"against": self.driver_cash_account,
				"credit": self.cash_amount,
				"credit_in_account_currency": self.cash_amount,
				"against_voucher": self.name,
				"against_voucher_type": self.doctype
			})

			paid_to_gl_entry = self.get_gl_dict({
				"account": self.driver_cash_account,
				"against": self.customer_name,
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
				"party": self.customer_name,
				"against": self.driver_cash_account,
				"credit": self.money_collection,
				"credit_in_account_currency": self.money_collection,
				"against_voucher": self.name,
				"against_voucher_type": self.doctype
                	})

			paid_to_gl_entry = self.get_gl_dict({
                        	"account": self.driver_cash_account,
                        	"against": self.customer_name,
                        	"debit": self.money_collection,
                        	"debit_in_account_currency": self.money_collection,
                        	"cost_center": self.cost_center
                	})

			make_gl_entries([customer_gl_entries, paid_to_gl_entry], cancel=(self.docstatus == 2),
				update_outstanding="Yes", merge_entries=False)



			

	def set_indicator(self):
		self.indicator_color = "orange"
                self.indicator_title = _("Unpaid")
#	def onload(self):

#		self.discounted_hop_no = frappe.db.get_single_value('Route Pricing Settings', 'hop_no_discounted')

#		self.hop_no_discounted  = frappe.db.get_value("Route Pricing Settings", "hop_no_discounted")
#		self.hop_no_discounted = frappe.db.sql("""
#                select hop_no_discounted from `tabRoute Pricing Settings`
#                where status = 'Active'
#                and (relieving_date is NULL or relieving_date >= %(from_date)s)
#                """, {"from_date": from_period}, as_dict=True)
#		self.hop_no_discounted  = 3

@frappe.whitelist()
def get_settings():

	DiscountedHopNo  = frappe.db.get_single_value('Route Pricing Settings', 'hop_no_discounted')
	HopNoToReturnForNormalRating  = frappe.db.get_single_value('Route Pricing Settings', 'return_to_normal_rating_hop_no')
	PriceForSecondHop  = frappe.db.get_single_value('Route Pricing Settings', 'second_hop_price')

#	no_hop = 4

	return DiscountedHopNo, HopNoToReturnForNormalRating, PriceForSecondHop


@frappe.whitelist()
def get_vehicle(AssignedDriver):
	assigned_vehicle = frappe.db.get_value('Vehicle', {'employee': AssignedDriver}, 'name')
	return assigned_vehicle


@frappe.whitelist()
def make_sales_invoice(dt, dn):



	doc = frappe.get_doc(dt, dn)
	if not frappe.db.get_value('Employee', {'name': doc.assigned_driver}, 'money_collection_account'):
		frappe.throw(_("Money Collection Account need to be set for Employee: {0} of the ID: {1}"). format(doc.driver_name, doc.assigned_driver))
        
	si_dn = frappe.db.get_value('Sales Invoice Item', {'trip_order': dn}, 'parent')
	if si_dn:
		return frappe.get_doc("Sales Invoice", si_dn)


#	doc = frappe.get_doc(dt, dn)
	child_doc_name = frappe.db.get_value('Taxi Hops', {'parent': dn}, 'name')
	child_doc = frappe.get_doc('Taxi Hops', child_doc_name)

	ToTheDestination =  frappe.db.sql("""
                select name, `to`, selected_metric, waiting, ozw, hop_price from `tabTaxi Hops` where parent like %(trip_dn)s order by idx""", {"trip_dn": dn})
#		in (select name from `tabSalary Slip`
#                where employee in (select employee from tabEmployee where board_member like %(brd_member)s)
#                and start_date >= %(from_date)s and end_date <= %(end_period)s and status = 'Submitted') 
#                and abbr = 'PFCSS'
#                """, {"brd_member": "Yes", "from_date": from_period, "end_period": to_period}, as_dict=True)


#	make_property_setter('Sales Invoice Item', "waiting", "in_list_view", 1, "Check")	
#	make_property_setter('Sales Invoice Item', "item_code", "columns", 2, "Int")	

#        si_dn = frappe.db.get_value('Sales Invoice Item', {'trip_order': dn}, 'parent')
#        if si_dn:
#                si = frappe.get_doc("Sales Invoice", si_dn)
#	else:
	si = frappe.new_doc("Sales Invoice")
	si.customer = doc.customer
	si.title = doc.customer
	si.type_of_order = "Trip Order"
	si.due_date = nowdate()

	for r in ToTheDestination:

		frappe.db.sql("""
                update `tabItem Price` set price_list_rate = %s where item_code = %s and selling = '1'""", (r[5], r[1]))
		frappe.db.commit()
#		frappe.msgprint(_("The result of For Loop are: {0}"). format(r[0]))
		waiting = str(r[3])
#		waiting = "0:00:00"		
#		frappe.msgprint(_("Waiting is: {0}"). format(waiting))
#		frappe.msgprint(_("OZY is: {0}"). format(r[3]))
#		frappe.msgprint(_("Hop Price: {0}"). format(r[4]))

		if waiting !="0:00:00":
#			note = "waiting= " + r[2]
			note = "waiting=" + waiting
			if int(r[4]) == 1:
				note = "ozw&" + note
		elif int(r[4]) == 1:
				note = "ozw"
		else:
			note = ""

#		frappe.msgprint(_("Note shape is: {0}"). format(note))
		si.append("items", {
                	"item_code": r[1],
                	"qty": "1",
			"rate": r[5],
			"price_list_rate": r[5],
#			"rate": "80000",
			"note": note,
                	"income_account": "Sales - GHYD",
                	"item_name": r[1],
                	"uom": "Unit",
                	"cost_center": "Main - GHYD",
                	"description": r[1],
			"to_detail": r[0],
			"trip_order": dn, 
                	"expense_account": "Cost of Goods Sold - GHYD"
        	})


		si.additional_discount_percentage = doc.discounted_percentage



			 
#        si.append("items", {
#                "item_code": "IPCCE",
#                "qty": "1",
#		"income_account": "Sales - GHYD",
#		"item_name": "IPCCE",
#		"uom": "Unit",
#		"cost_center": "Main - GHYD",
#		"description": "IPCCE",
#		"expense_account": "Cost of Goods Sold - GHYD"
#        })

#	frappe.msgprint(_("The To's are: {0}"). format(ToTheDestination[0]))
#	frappe.msgprint(_("The Taxi Hops Child Name is: {0}"). format(child_doc_name))
	
	si.save()
	si.submit()

        return si


@frappe.whitelist()
def make_payment_entry(si_dn, to_dn):
        
	si_doc = frappe.get_doc("Sales Invoice", si_dn)
	to_doc = frappe.get_doc("Trip Order", to_dn)
#	child_doc_name = frappe.db.get_value('Taxi Hops', {'parent': dn}, 'name')
#	child_doc = frappe.get_doc('Taxi Hops', child_doc_name)

#	ToTheDestination =  frappe.db.sql("""
#                select `to`, selected_metric, waiting, ozw, hop_price from `tabTaxi Hops` where parent like %(trip_dn)s order by idx""", {"trip_dn": dn})
#		in (select name from `tabSalary Slip`
#                where employee in (select employee from tabEmployee where board_member like %(brd_member)s)
#                and start_date >= %(from_date)s and end_date <= %(end_period)s and status = 'Submitted') 
#                and abbr = 'PFCSS'
#                """, {"brd_member": "Yes", "from_date": from_period, "end_period": to_period}, as_dict=True)


#	make_property_setter('Sales Invoice Item', "waiting", "in_list_view", 1, "Check")	
#	make_property_setter('Sales Invoice Item', "item_code", "columns", 2, "Int")	
	pe = frappe.new_doc("Payment Entry")
	pe.company = si_doc.company
	pe.posting_date = nowdate()
	pe.party_type = "Customer"
	pe.mode_of_payment = "Cash"
	pe.party = si_doc.customer
	pe.party_name = pe.party
	pe.party_balance = get_balance_on(party_type="Customer", party=pe.party)
	pe.paid_from = get_party_account("Customer", pe.party, si_doc.company)
	pe.paid_from_account_balance = get_balance_on(pe.paid_from, date=pe.posting_date)
	from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
#	pe.paid_to = get_bank_cash_account(pe.mode_of_payment, pe.company)['account']
	pe.paid_to = frappe.db.get_value('Employee', {'name': to_doc.assigned_driver}, 'money_collection_account')
	pe.paid_to_account_balance = get_balance_on(pe.paid_to, date=pe.posting_date)
#	pe.paid_to = frappe.db.get_value("Mode of Payment Account", {"parent": pe.mode_of_payment, "company": pe.company}, "default_account")
	pe.paid_from_account_currency = "LBP"
	pe.paid_to_account_currency = "LBP"
#	pe.source_exchange_rate = 1.0
	pe.paid_amount = to_doc.cash_amount + to_doc.money_collection
	pe.received_amount = pe.paid_amount
	pe.allocate_payment_amount = 1
	pe.title = si_doc.customer

        pe.append("references", {
                "reference_doctype": "Sales Invoice",
                "reference_name": si_dn,
                "due_date": si_doc.get("due_date"),
                "total_amount": si_doc.grand_total,
                "outstanding_amount": si_doc.outstanding_amount,
                "allocated_amount": to_doc.cash_amount
        })



	if to_doc.money_collection > 0:

		from erpnext.accounts.doctype.payment_entry.payment_entry import get_outstanding_reference_documents

        	args = {"posting_date": pe.posting_date, "company": pe.company, "party_type": pe.party_type, "payment_type": pe.payment_type, "party": pe.party, "party_account": pe.paid_from}
        	outstanding_docs = []
        	outstanding_docs = get_outstanding_reference_documents(args)

		frappe.msgprint(_("Outstanding are: {0}").format(outstanding_docs))
		frappe.msgprint(_("Outstanding are: {0}").format(outstanding_docs[0]))
		frappe.msgprint(_("Outstanding are: {0}").format(outstanding_docs[1]))
		frappe.msgprint(_("Outstanding are: {0}").format(outstanding_docs[0]["due_date"]))
		frappe.msgprint(_("Outstanding are: {0}").format(len(outstanding_docs)))

		_money_collection = to_doc.money_collection

		for d in outstanding_docs:
		
			if d.voucher_no != si_dn and d.voucher_type == "Sales Invoice":

				if _money_collection > d.outstanding_amount:
					outstanding = d.outstanding_amount
					_money_collection = _money_collection - d.outstanding_amount
				else:
					outstanding = _money_collection
					_money_collection = 0
				pe.append("references", {
				"reference_doctype": "Sales Invoice",
				"reference_name": d.voucher_no,
				"due_date": d.due_date,
				"total_amount": d.invoice_amount,
				"outstanding_amount": d.outstanding_amount,
				"allocated_amount": outstanding
        			})
			if _money_collection == 0:
				break


	total_allocated_amount, base_total_allocated_amount = 0, 0

	for d in pe.get("references"):
		if d.allocated_amount:
			total_allocated_amount += flt(d.allocated_amount)

	pe.total_allocated_amount = abs(total_allocated_amount)
	pe.base_total_allocated_amount = pe.total_allocated_amount

#	pe.type_of_order = "Trip Order"
#	pe.posting_date = nowdate()

#	for r in ToTheDestination:

#		frappe.db.sql("""
#                update `tabItem Price` set price_list_rate = %s where item_code = %s and selling = '1'""", (r[4], r[0]))
#		frappe.db.commit()
#		frappe.msgprint(_("The result of For Loop are: {0}"). format(r[0]))
#		waiting = str(r[2])
#		waiting = "0:00:00"		
#		frappe.msgprint(_("Waiting is: {0}"). format(waiting))
#		frappe.msgprint(_("OZY is: {0}"). format(r[3]))
#		frappe.msgprint(_("Hop Price: {0}"). format(r[4]))

#		if waiting !="0:00:00":
#			note = "waiting= " + r[2]
#			note = "waiting=" + waiting
#			if int(r[3]) == 1:
#				note = "ozw&" + note
#		elif int(r[3]) == 1:
#				note = "ozw"
#		else:
#			note = ""

#		frappe.msgprint(_("Note shape is: {0}"). format(note))
#		pe.append("items", {
#                	"item_code": r[0],
#                	"qty": "1",
#			"rate": r[4],
#			"price_list_rate": r[4],
#			"rate": "80000",
#			"note": note,
#                	"income_account": "Sales - GHYD",
#                	"item_name": r[0],
#                	"uom": "Unit",
#                	"cost_center": "Main - GHYD",
#                	"description": r[0],
#                	"expense_account": "Cost of Goods Sold - GHYD"
#        	})



			 
#        si.append("items", {
#                "item_code": "IPCCE",
#                "qty": "1",
#		"income_account": "Sales - GHYD",
#		"item_name": "IPCCE",
#		"uom": "Unit",
#		"cost_center": "Main - GHYD",
#		"description": "IPCCE",
#		"expense_account": "Cost of Goods Sold - GHYD"
#        })

#	frappe.msgprint(_("The To's are: {0}"). format(ToTheDestination[0]))
#	frappe.msgprint(_("The Taxi Hops Child Name is: {0}"). format(child_doc_name))
	
#	pe.flags.ignore_validate = True
#	pe.flags.ignore_permissions = True
	pe.save()
	pe.submit()

        return pe


# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bilal Ghayad and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document, _
#from erpnext.controllers.selling_controller import SellingController
from frappe import utils
from erpnext.accounts.utils import get_outstanding_invoices, get_account_currency, get_balance_on
from datetime import datetime, date
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.accounts.general_ledger import delete_gl_entries

#class ClearanceWithDriver(Document):
class ClearanceWithDriver(AccountsController):
#class ClearanceWithDriver(SellingController):

#	pass

        def validate(self):
                self.title = self.driver_name
		if (self.clearance_date < self.last_clearance_date):	
               		frappe.throw(_("Clearance Date can not be before Last Clearance Date"))
#		self.clearance_date = utils.now()
#                if (self.credit_amount > 0 and self.money_collection > 0):
#                	frappe.throw(_("Can not set money collection amount > 0 if credit amount > 0, please correct"))


        def on_cancel(self):
                delete_gl_entries(voucher_type=self.doctype, voucher_no=self.name)

		to_clr_count = frappe.db.sql("""update `tabTrip Order` set driver_clearance_status = "No"
			where name in (select trip_order from `tabClearance With Driver Trips Orders` where parent = %s)
			""", (self.name), as_dict=True)


        def on_submit(self):
		if not (self.receiving_payment_account) or not (self.account_paid_from) or not (self.expenses_account) :
                	frappe.throw(_("All Transactions Accounts need to be filled to be able to submit"))

		self.update_to_clearance()
		
		self.posting_date = self.clearance_date
		self.make_gl_entries()


	def update_to_clearance(self):

		to_clr_count = frappe.db.sql("""update `tabTrip Order` set driver_clearance_status = "Yes"
			where name in (select trip_order from `tabClearance With Driver Trips Orders` where parent = %s)
			""", (self.name), as_dict=True)


	def make_gl_entries(self):

		if (self.amount_to_us > 0 and self.amount_to_driver == 0):

			pay_to_gl_entry =  self.get_gl_dict({
				"account": self.expenses_account,
				"party_type": "Employee",
				"party": self.driver,
				"against": self.driver_cash_account,
				"debit": self.amount_due_to_driver_cal,
				"debit_in_account_currency": self.amount_due_to_driver_cal,
				"voucher_no": self.name,
				"cost_center": self.cost_center
			})

			from_driver_gl_entry = self.get_gl_dict({
				"account": self.driver_cash_account,
				"against": self.driver,
				"credit": self.amount_due_to_driver_cal,
				"credit_in_account_currency": self.amount_due_to_driver_cal,
				"against_voucher": self.name,
				"against_voucher_type": self.doctype,
				"cost_center": self.cost_center
			})

			if (self.amount_due_to_driver_cal > 0):
	                	make_gl_entries([pay_to_gl_entry, from_driver_gl_entry], cancel=(self.docstatus == 2),	
        	                	update_outstanding="Yes", merge_entries=False)

			rec_pay_gl_entry =  self.get_gl_dict({
				"account": self.receiving_payment_account,
				"against": self.driver_cash_account,
				"debit": self.amount_to_us,
				"debit_in_account_currency": self.amount_to_us,
				"voucher_no": self.name,
				"cost_center": self.cost_center
			})


			from_driver_gl_entry = self.get_gl_dict({
				"account": self.driver_cash_account,
				"against": self.receiving_payment_account,
				"credit": self.amount_to_us,
				"credit_in_account_currency": self.amount_to_us,
				"against_voucher": self.name,
				"against_voucher_type": self.doctype,
				"cost_center": self.cost_center
			})

			make_gl_entries([rec_pay_gl_entry, from_driver_gl_entry], cancel=(self.docstatus == 2),
                        	update_outstanding="Yes", merge_entries=False)

		elif (self.amount_to_driver > 0 and self.amount_to_us == 0):
			
			pay_to_gl_entry =  self.get_gl_dict({
				"account": self.expenses_account,
				"party_type": "Employee",
				"party": self.driver,
				"against": self.driver_cash_account,
				"debit": self.cash_with_him,
				"debit_in_account_currency": self.cash_with_him,
				"voucher_no": self.name,
				"cost_center": self.cost_center
			})

			from_driver_gl_entry = self.get_gl_dict({
				"account": self.driver_cash_account,
				"against": self.driver,
				"credit": self.cash_with_him,
				"credit_in_account_currency": self.cash_with_him,
				"against_voucher": self.name,
				"against_voucher_type": self.doctype,
				"cost_center": self.cost_center
			})


			if (self.cash_with_him > 0.5):
	                        make_gl_entries([pay_to_gl_entry, from_driver_gl_entry], cancel=(self.docstatus == 2),
        	                        update_outstanding="Yes", merge_entries=False)

			pay_to_gl_entry =  self.get_gl_dict({
				"account": self.expenses_account,
				"party_type": "Employee",
				"party": self.driver,
				"against": self.account_paid_from,
				"debit": self.amount_to_driver,
				"debit_in_account_currency": self.amount_to_driver,
				"voucher_no": self.name,
				"voucher_type": self.doctype,
				"cost_center": self.cost_center
			})


			pay_from_gl_entry = self.get_gl_dict({
				"account": self.account_paid_from,
				"against": self.driver,
				"credit": self.amount_to_driver,
				"credit_in_account_currency": self.amount_to_driver,
				"voucher_no": self.name,
				"voucher_type": self.doctype,
				"cost_center": self.cost_center
			})

                        make_gl_entries([pay_to_gl_entry, pay_from_gl_entry], cancel=(self.docstatus == 2),
                                update_outstanding="Yes", merge_entries=False)



@frappe.whitelist()
def get_driver_info(driver):


	emp_type = frappe.db.get_value('Employee', {'name': driver}, 'employment_type')
	emp_name = frappe.db.get_value('Employee', {'name': driver}, 'employee_name')

	return emp_type, emp_name

@frappe.whitelist()
def get_clr_strt(driver, clearance_date=None):

	assigned_vehicle = frappe.db.get_value('Vehicle', {'employee': driver}, 'name')

	mny_col_drv_acc = frappe.db.get_value('Employee', {'name': driver}, 'money_collection_account')

	clr_date = datetime.now()
	if (clearance_date == None):
		csh_with_drv = get_balance_on(mny_col_drv_acc, date=clr_date)
	else:
		csh_with_drv = get_balance_on(mny_col_drv_acc, date=clearance_date)
#		clearance_date = datetime.datetime.now()
#		frappe.msgprint(_("Clearance Date is: {0}"). format(clearance_date))
#	frappe.msgprint(_("Assigned Vehicle: {0}"). format(assigned_vehicle))

# If it is the first clearance, then start date for the clearance is the joining date
	joining_date = frappe.db.get_value('Employee', {"name": driver} ,'date_of_joining')
	clr_strt_date = joining_date
	clr_strt_date = datetime.combine(clr_strt_date, datetime.min.time())
	clr_strt_date = clr_strt_date.replace(hour=00, minute=01, second=00)
	last_clr_date = frappe.db.sql("""select clearance_date from `tabClearance With Driver` where driver = %s and docstatus = 1
		order by clearance_date desc limit 1""", (driver), as_dict=True)

# If there is a clearance before, then its date is the start date for the new clearance
	if (len(last_clr_date) > 0):
		clr_strt_date = last_clr_date[0]['clearance_date']

	last_payment_date = frappe.db.sql(""" select posting_date from `tabPayment Entry`
                                where payment_type = "Internal Transfer" and paid_from = (select money_collection_account from `tabEmployee` where name = %s)
                                and paid_to in (select default_cash_account from `tabCompany`)
                                and docstatus = 1 order by posting_date desc limit 1
                                """, (driver), as_dict=True)

#	frappe.msgprint(_("Cash With Him is: {0}"). format(CashWithHim))
#	frappe.msgprint(_("Joining Date: {0}"). format(ClrStrtDate))
	return assigned_vehicle, last_payment_date, last_clr_date, clr_strt_date, csh_with_drv, clr_date


@frappe.whitelist()
def get_values(driver, clearance_date):

#	frappe.msgprint(_("Welcome: {0}"). format(AssignedDriver))

	joining_date = frappe.db.get_value('Employee', {"name": driver} ,'date_of_joining')
	clr_strt_date = joining_date
	clr_strt_date = datetime.combine(clr_strt_date, datetime.min.time())
	clr_strt_date = clr_strt_date.replace(hour=00, minute=01, second=00)

#	frappe.msgprint(_("Clearance Start Date: {0}"). format(clr_strt_date))

	mny_col_drv_acc = frappe.db.get_value('Employee', {'name': driver}, 'money_collection_account')

	csh_with_drv = get_balance_on(mny_col_drv_acc, date=clearance_date)
	if (not csh_with_drv):
		csh_with_drv = 0
# Still last payment need modification, it has to get the last payment for the employee, so it is required to get the money collection account of the employee.

	last_acr = frappe.db.sql(""" select name, commission_rule, commission_percent, weekly_fees from `tabAssign Commission Rule`
                                where driver = %s and docstatus = 1 order by modified desc limit 1
                                """, (driver), as_dict=True)


	last_payment_date = frappe.db.sql(""" select posting_date from `tabPayment Entry`
                                where payment_type = "Internal Transfer" and paid_from = (select money_collection_account from `tabEmployee` where name = %s)
                                and paid_to in (select default_cash_account from `tabCompany`)
                                and docstatus = 1 order by posting_date desc limit 1
                                """, (driver), as_dict=True)
# Still need to confirm if the date to be the last modified or the created, and it is required to set the clearance date based on that.

	last_clearance_date = frappe.db.sql("""select clearance_date from `tabClearance With Driver` where driver = %s and docstatus = 1 
			order by clearance_date desc limit 1""", (driver), as_dict=True)

# If there there is a previous clearance, then the start date of this clearance is the date of the previous clearance

	if (len(last_clearance_date) > 0):
		clr_strt_date = last_clearance_date[0]['clearance_date']


	to_statement = frappe.db.sql("""
			select name, title, posting_date, grand_total, cash_amount, credit_amount, 
			money_collection, driver_compensation, total_price_for_subscription_order, driver_clearance_status from `tabTrip Order`
			where assigned_driver = %s and posting_date <= %s and driver_clearance_status not like "Yes" and driver_clearance_status is not NULL 
			and docstatus = 1 order by posting_date desc
			""", (driver, clearance_date), as_dict=True)

	maint_statement = frappe.db.sql("""select name, total_claimed_amount, total_sanctioned_amount, vehicle_log, employee 
			from `tabExpense Claim` where employee = %s and posting_date > %s and posting_date <= %s  and docstatus = 1
			""", (driver, clr_strt_date, clearance_date), as_dict=True)

	total_maint = frappe.db.sql("""select sum(total_sanctioned_amount) as sum_total_sanctioned 
			from `tabExpense Claim` where employee = %s and posting_date > %s and posting_date <= %s  and docstatus = 1
			""", (driver, clr_strt_date, clearance_date), as_dict=True)


	maint_exp_claim = frappe.db.sql(""" select name from `tabExpense Claim` 
			where employee = %s and posting_date > %s and posting_date <= %s and docstatus = 1
			""", (driver, clr_strt_date, clearance_date), as_dict=True)


	total_paid_maint = frappe.db.sql(""" select COALESCE(sum(total_allocated_amount),0) as total_maint from `tabPayment Entry`
				where name in (select parent from `tabPayment Entry Reference` where reference_name in 
				(select name from `tabExpense Claim` where employee = %s and docstatus = 1))
				and posting_date > %s and posting_date <= %s and docstatus = 1
				""", (driver, clr_strt_date, clearance_date), as_dict=True)


	total_mon_col_out_order = frappe.db.sql(""" select COALESCE(sum(received_amount),0) as total_col_mon_out from `tabPayment Entry`
				where payment_type = "Receive" and paid_to = (select money_collection_account from `tabEmployee` where name = %s) 
				and party_type = "Customer" and posting_date > %s and posting_date <= %s and docstatus = 1
				""", (driver, clr_strt_date, clearance_date), as_dict=True)


	total_delivered_mon = frappe.db.sql(""" select COALESCE(sum(received_amount),0) as total_delivered_mon from `tabPayment Entry`
                                where payment_type = "Internal Transfer" and paid_from = (select money_collection_account from `tabEmployee` where name = %s)
                                and paid_to in (select default_cash_account from `tabCompany`)
                                and  posting_date > %s and posting_date <= %s and docstatus = 1
                                """, (driver, clr_strt_date, clearance_date), as_dict=True)


#	frappe.msgprint(_("Clearance Start Date: {0}"). format(clr_strt_date))
#	frappe.msgprint(_("Maintenance Statement: {0}"). format(maint_statement))
#	frappe.msgprint(_("Maintenance Statement: {0}"). format(total_maint[0]['sum_total_sanctioned']))
#	frappe.msgprint(_("Maintenance Expense Claim: {0}"). format(maint_exp_claim))
#	frappe.msgprint(_("Total Payment For Maintenance: {0}"). format (total_paid_maint[0]['total_maint']))
#	frappe.msgprint(_("Total Payments From Customers out of the orders: {0}"). format (total_mon_col_out_order[0]['total_col_mon_out']))
#	frappe.msgprint(_("Total Delivered Money for Office: {0}"). format (total_delivered_mon[0]['total_delivered_mon']))


        return mny_col_drv_acc, csh_with_drv, last_payment_date, last_clearance_date, to_statement, total_paid_maint, maint_statement, total_maint, total_mon_col_out_order, total_delivered_mon, joining_date, clr_strt_date, last_acr

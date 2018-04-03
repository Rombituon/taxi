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
from erpnext.accounts.general_ledger import delete_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.accounts.general_ledger import make_gl_entries

# test
# New test for merge
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


        def on_submit(self):
		if not (self.receiving_payment_account) or not (self.account_paid_from) or not (self.expenses_account) :
                	frappe.throw(_("All Transactions Accounts need to be filled to be able to submit"))
		
		self.posting_date = self.clearance_date
		self.make_gl_entries()


	def make_gl_entries(self):

		rec_pay_gl_entries =  self.get_gl_dict({
        		"account": self.receiving_payment_account,
#                	"party_type": "Employee",
#                	"party": self.driver,
                	"against": self.driver_cash_account,
                	"debit": self.amount_due_to_us,
                	"debit_in_account_currency": self.amount_due_to_us,
#			"voucher_no": self.name,
#                	"against_voucher": self.name,
#			"against_voucher_type": self.doctype
		})

                from_emp_gl_entry = self.get_gl_dict({
                        "account": self.driver_cash_account,
                        "against": self.driver,
                        "credit": self.amount_due_to_us,
                        "credit_in_account_currency": self.amount_due_to_us,
                	"against_voucher": self.name,
			"against_voucher_type": self.doctype
#			"voucher_no": self.name
#                        "cost_center": self.cost_center
                })

                pay_to_gl_entries =  self.get_gl_dict({
                        "account": self.expenses_account,
                        "party_type": "Employee",
                        "party": self.driver,
                        "against": self.account_paid_from,
                        "debit": self.amount_due_to_driver,
                        "debit_in_account_currency": self.amount_due_to_driver,
#			"voucher_no": self.name
                        "against_voucher": self.name,
                        "against_voucher_type": self.doctype,
			"cost_center": self.cost_center
                })

                pay_from_gl_entry = self.get_gl_dict({
                        "account": self.account_paid_from,
                        "against": self.driver,
                        "credit": self.amount_due_to_us,
                        "credit_in_account_currency": self.amount_due_to_us,
#			"voucher_no": self.name
#                        "cost_center": self.cost_center
                })


		if (self.amount_due_to_us > 0 and self.amount_due_to_driver == 0):

                	rec_pay_gl_entries =  self.get_gl_dict({
                        	"account": self.receiving_payment_account,
#                       	"party_type": "Employee",
#                       	"party": self.driver,
                        	"against": self.driver_cash_account,
                        	"debit": self.amount_due_to_us,
                        	"debit_in_account_currency": self.amount_due_to_us
#                       	"voucher_no": self.name,
#                       	"against_voucher": self.name,
#                       	"against_voucher_type": self.doctype
                	})

                	from_emp_gl_entry = self.get_gl_dict({
                        	"account": self.driver_cash_account,
                        	"against": self.receiving_payment_account,
                        	"credit": self.amount_due_to_us,
                        	"credit_in_account_currency": self.amount_due_to_us,
                        	"against_voucher": self.name,
                        	"against_voucher_type": self.doctype
#                       	"voucher_no": self.name
#                        	"cost_center": self.cost_center
                	})


                	make_gl_entries([rec_pay_gl_entries, from_emp_gl_entry], cancel=(self.docstatus == 2),
                        	update_outstanding="Yes", merge_entries=False)


		elif (self.amount_due_to_driver > 0 and (self.cash_with_him  >= self.amount_due_to_driver)):
			
                        pay_from_gl_entry = self.get_gl_dict({
                                "account": self.driver_cash_account,
                                "against": self.driver,
                                "credit": self.amount_due_to_driver,
                                "credit_in_account_currency": self.amount_due_to_driver
#                               "voucher_no": self.name
#                               "cost_center": self.cost_center
                        })


                	pay_to_gl_entries =  self.get_gl_dict({
                        	"account": self.expenses_account,
                        	"party_type": "Employee",
                        	"party": self.driver,
                        	"against": self.driver_cash_account,
                        	"debit": self.amount_due_to_driver,
                        	"debit_in_account_currency": self.amount_due_to_driver,
#                       	"voucher_no": self.name
                        	"against_voucher": self.name,
                        	"against_voucher_type": self.doctype,
				"cost_center": self.cost_center
                	})


                        make_gl_entries([pay_from_gl_entry, pay_to_gl_entries], cancel=(self.docstatus == 2),
                                update_outstanding="Yes", merge_entries=False)



			if (self.cash_with_him - self.amount_due_to_driver > 0.5):


                		from_emp_gl_entry = self.get_gl_dict({
                        		"account": self.driver_cash_account,
                        		"against": self.receiving_payment_account,
                        		"credit": self.amount_due_to_us,
                        		"credit_in_account_currency": self.amount_due_to_us,
                        		"against_voucher": self.name,
                        		"against_voucher_type": self.doctype
#                       		"voucher_no": self.name
#                        		"cost_center": self.cost_center
                		})

                        	rec_pay_gl_entries =  self.get_gl_dict({
                                	"account": self.receiving_payment_account,
#                               	"party_type": "Employee",
#                               	"party": self.driver,
                                	"against": self.driver_cash_account,
                                	"debit": self.amount_due_to_us,
                                	"debit_in_account_currency": self.amount_due_to_us
#                               	"voucher_no": self.name,
#                               	"against_voucher": self.name,
#                              		"against_voucher_type": self.doctype
                        	})


				make_gl_entries([from_emp_gl_entry, rec_pay_gl_entries], cancel=(self.docstatus == 2),
        	                update_outstanding="Yes", merge_entries=False)

		elif (self.amount_due_to_driver > 0 and (self.cash_with_him  < self.amount_due_to_driver)):

                        from_emp_gl_entry = self.get_gl_dict({
                                "account": self.driver_cash_account,
                                "against": self.driver,
                                "credit": self.cash_with_him,
                                "credit_in_account_currency": self.cash_with_him,
                                "against_voucher": self.name,
                                "against_voucher_type": self.doctype
                        })

                        pay_to_gl_entries =  self.get_gl_dict({
                                "account": self.expenses_account,
                                "party_type": "Employee",
                                "party": self.driver,
                                "against": self.driver_cash_account,
                                "debit": self.cash_with_him,
                                "debit_in_account_currency": self.cash_with_him,
                                "against_voucher": self.name,
                                "against_voucher_type": self.doctype,
				"cost_center": self.cost_center
                        })


                        make_gl_entries([from_emp_gl_entry, pay_to_gl_entries], cancel=(self.docstatus == 2),
                                update_outstanding="Yes", merge_entries=False)

#			frappe.msgprint(_("I am at this point: {0}"). format(self.amount_due_to_driver - self.cash_with_him))


			if (self.amount_due_to_driver - self.cash_with_him > 0.5):

	                        pay_from_gl_entry = self.get_gl_dict({
        	                        "account": self.account_paid_from,
                	                "against": self.driver,
                        	        "credit": (self.amount_due_to_driver - self.cash_with_him),
                                	"credit_in_account_currency": (self.amount_due_to_driver - self.cash_with_him)
#                               	"voucher_no": self.name
#                               	"cost_center": self.cost_center
                        	})


                        	pay_to_gl_entries =  self.get_gl_dict({
                                	"account": self.expenses_account,
	                                "party_type": "Employee",
        	                        "party": self.driver,
                	                "against": self.account_paid_from,
                        	        "debit": (self.amount_due_to_driver - self.cash_with_him),
	                                "debit_in_account_currency": (self.amount_due_to_driver - self.cash_with_him),
        	                        "against_voucher": self.name,
                	                "against_voucher_type": self.doctype,
					"cost_center": self.cost_center
                        	})

                        	make_gl_entries([pay_from_gl_entry, pay_to_gl_entries], cancel=(self.docstatus == 2),
                                	update_outstanding="Yes", merge_entries=False)




@frappe.whitelist()
def GetClrVehStrt(driver, clearance_date=None):

        assigned_vehicle = frappe.db.get_value('Vehicle', {'employee': driver}, 'name')

	MnyColDrvAcc = frappe.db.get_value('Employee', {'name': driver}, 'money_collection_account')

	CLRDate = datetime.now()
	if (clearance_date == None):
		CshWithDrv = get_balance_on(MnyColDrvAcc, date=CLRDate)
	else:
		CshWithDrv = get_balance_on(MnyColDrvAcc, date=clearance_date)
#		clearance_date = datetime.datetime.now()
#		frappe.msgprint(_("Clearance Date is: {0}"). format(clearance_date))
#	MoneyCollectionDriverAccount = frappe.db.get_value('Employee', {'name': driver}, 'money_collection_account')
#	CashWithHim = get_balance_on(MoneyCollectionDriverAccount, date=clearance_date)
#	frappe.msgprint(_("Cash With Him is: {0}"). format(CashWithHim))
#	frappe.msgprint(_("Assigned Vehicle: {0}"). format(assigned_vehicle))
        JoiningDate = frappe.db.get_value('Employee', {"name": driver} ,'date_of_joining')
        ClrStrtDate = JoiningDate
        ClrStrtDate = datetime.combine(ClrStrtDate, datetime.min.time())
        ClrStrtDate = ClrStrtDate.replace(hour=00, minute=01, second=00)

        LastClr = frappe.db.sql("""select modified from `tabClearance With Driver` where driver = %s and docstatus = 1
		order by modified desc limit 1""", (driver), as_dict=True)

        if (len(LastClr) > 0):
                ClrStrtDate = LastClr[0]['modified']

#        LastPayment =  frappe.db.sql("""select creation from `tabPayment Entry` order by creation desc limit 1""", as_dict=True)

        LastPayment = frappe.db.sql(""" select modified from `tabPayment Entry`
                                where payment_type = "Internal Transfer" and paid_from = (select money_collection_account from `tabEmployee` where name = %s)
                                and paid_to in (select default_cash_account from `tabCompany`)
                                and docstatus = 1 order by modified desc limit 1
                                """, (driver), as_dict=True)



#	frappe.msgprint(_("Cash With Him is: {0}"). format(CashWithHim))
#	frappe.msgprint(_("Joining Date: {0}"). format(ClrStrtDate))
        return assigned_vehicle, LastPayment, LastClr, ClrStrtDate, CshWithDrv, CLRDate


@frappe.whitelist()
def get_values(driver, clearance_date):

#	frappe.msgprint(_("Welcome: {0}"). format(AssignedDriver))

	HiringDate = frappe.db.get_value('Employee', {"name": driver} ,'date_of_joining')
	EmpType = frappe.db.get_value('Employee', {"name": driver} ,'employment_type')
		

	clr_strt_date = HiringDate
	clr_strt_date = datetime.combine(clr_strt_date, datetime.min.time())
	clr_strt_date = clr_strt_date.replace(hour=00, minute=01, second=00)

#	frappe.msgprint(_("Clearance Start Date: {0}"). format(clr_strt_date))

	MoneyCollectionDriverAccount = frappe.db.get_value('Employee', {'name': driver}, 'money_collection_account')

	CashWithHim = get_balance_on(MoneyCollectionDriverAccount, date=clearance_date)
	if (not CashWithHim):
		CashWithHim = 0
# Still last payment need modification, it has to get the last payment for the employee, so it is required to get the money collection account of the employee.

        LastACR = frappe.db.sql(""" select name, commission_rule, commission_percent, weekly_fees from `tabAssign Commission Rule`
                                where driver = %s and docstatus = 1 order by modified desc limit 1
                                """, (driver), as_dict=True)


        LastPayment = frappe.db.sql(""" select modified from `tabPayment Entry`
                                where payment_type = "Internal Transfer" and paid_from = (select money_collection_account from `tabEmployee` where name = %s)
                                and paid_to in (select default_cash_account from `tabCompany`)
                                and docstatus = 1 order by modified desc limit 1
                                """, (driver), as_dict=True)
# Still need to confirm if the date to be the last modified or the created, and it is required to set the clearance date based on that.

	LastClearance = frappe.db.sql("""select modified from `tabClearance With Driver` where driver = %s and docstatus = 1 
			order by modified desc limit 1""", (driver), as_dict=True)

	if (len(LastClearance) > 0):
		clr_strt_date = LastClearance[0]['modified']


	to_statement = frappe.db.sql("""select name, title, creation, grand_total, cash_amount, credit_amount, driver_clearance_status from `tabTrip Order`
			where assigned_driver = %s and modified < %s and driver_clearance_status not like "Yes" and driver_clearance_status is not NULL 
			and docstatus = 1 order by creation desc limit 5""", (driver, clearance_date), as_dict=True)

	maint_statement = frappe.db.sql("""select name, total_claimed_amount, total_sanctioned_amount, vehicle_log, employee 
			from `tabExpense Claim` where employee = %s and modified > %s and modified < %s  and docstatus = 1
			""", (driver, clr_strt_date, clearance_date), as_dict=True)

	total_maint = frappe.db.sql("""select sum(total_sanctioned_amount) as sum_total_sanctioned 
			from `tabExpense Claim` where employee = %s and modified > %s and modified < %s  and docstatus = 1
			""", (driver, clr_strt_date, clearance_date), as_dict=True)


	maint_exp_claim = frappe.db.sql(""" select name from `tabExpense Claim` 
			where employee = %s and modified > %s and modified < %s  and docstatus = 1
			""", (driver, clr_strt_date, clearance_date), as_dict=True)


	total_paid_maint = frappe.db.sql(""" select COALESCE(sum(total_allocated_amount),0) as total_maint from `tabPayment Entry`
				where name in (select parent from `tabPayment Entry Reference` where reference_name in 
				(select name from `tabExpense Claim` where employee = %s and  modified > %s and modified < %s  and docstatus = 1))
				""", (driver, clr_strt_date, clearance_date), as_dict=True)


	total_mon_col_out_order = frappe.db.sql(""" select COALESCE(sum(received_amount),0) as total_col_mon_out from `tabPayment Entry`
				where payment_type = "Receive" and paid_to = (select money_collection_account from `tabEmployee` where name = %s) 
				and party_type = "Customer" and docstatus = 1 and modified > %s and modified < %s
				""", (driver, clr_strt_date, clearance_date), as_dict=True)


        total_delivered_mon = frappe.db.sql(""" select COALESCE(sum(received_amount),0) as total_delivered_mon from `tabPayment Entry`
                                where payment_type = "Internal Transfer" and paid_from = (select money_collection_account from `tabEmployee` where name = %s)
                                and paid_to in (select default_cash_account from `tabCompany`)
                                and docstatus = 1
                                """, (driver), as_dict=True)


#	frappe.msgprint(_("Clearance Start Date: {0}"). format(clr_strt_date))
#	frappe.msgprint(_("Maintenance Statement: {0}"). format(maint_statement))
#	frappe.msgprint(_("Maintenance Statement: {0}"). format(total_maint[0]['sum_total_sanctioned']))
#	frappe.msgprint(_("Maintenance Expense Claim: {0}"). format(maint_exp_claim))
#	frappe.msgprint(_("Total Payment For Maintenance: {0}"). format (total_paid_maint[0]['total_maint']))
#	frappe.msgprint(_("Total Payments From Customers out of the orders: {0}"). format (total_mon_col_out_order[0]['total_col_mon_out']))
#	frappe.msgprint(_("Total Delivered Money for Office: {0}"). format (total_delivered_mon[0]['total_delivered_mon']))


        return MoneyCollectionDriverAccount, CashWithHim, LastPayment, LastClearance, to_statement, total_paid_maint, maint_statement, total_maint, total_mon_col_out_order, total_delivered_mon, HiringDate, clr_strt_date, LastACR

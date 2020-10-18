
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals

import erpnext
import frappe
from frappe import _
import random
from frappe.utils import random_string, getdate
from frappe.desk import query_report
from erpnext.accounts.doctype.journal_entry.journal_entry import get_payment_entry_against_invoice
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from frappe.utils.make_random import get_random
from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request, make_payment_entry
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice

def run():
	frappe.set_user("thierry@dokos.io")
	frappe.set_user_lang("fr")

	if random.random() <= 0.6:
		sales_orders = frappe.get_all("Sales Order", filters={"per_billed": ("<", 100)})
		for so in sales_orders[:random.randint(1, 5)]:
			try:
				si = frappe.get_doc(make_sales_invoice(so))
				si.set_posting_time = True
				si.posting_date = frappe.flags.current_date
				si.payment_schedule = []
				for d in si.get("items"):
					if not d.income_account:
						d.income_account = "Sales - {}".format(frappe.get_cached_value('Company',  si.company,  'abbr'))
				si.insert()
				si.submit()
				frappe.db.commit()
			except frappe.ValidationError:
				pass
			except erpnext.accounts.utils.FiscalYearError:
				add_fiscal_year(frappe.flags.current_date)

	# TODO
	"""
	if random.random() <= 0.6:
		report = "Received Items to be Billed"
		for pr in list(set([r[0] for r in query_report.run(report)["result"]
			if r[0]!="Total"]))[:random.randint(1, 5)]:
			try:
				pi = frappe.get_doc(make_purchase_invoice(pr))
				pi.set_posting_time = True
				pi.posting_date = frappe.flags.current_date
				pi.bill_no = random_string(6)
				pi.insert()
				pi.submit()
				frappe.db.commit()
			except frappe.ValidationError:
				pass
	"""


	if random.random() < 0.5:
		make_payment_entries("Sales Invoice", "Accounts Receivable")

	# TODO
	"""
	if random.random() < 0.5:
		make_payment_entries("Purchase Invoice", "Accounts Payable")
	"""

def make_payment_entries(ref_doctype, report):
	outstanding_invoices = frappe.get_all(ref_doctype, fields=["name"],
		filters={
			"company": erpnext.get_default_company(),
			"outstanding_amount": (">", 0.0)
		})

	# make Payment Entry
	for inv in outstanding_invoices[:random.randint(1, 2)]:
		pe = get_payment_entry(ref_doctype, inv.name)
		pe.posting_date = frappe.flags.current_date
		pe.reference_no = random_string(6)
		pe.reference_date = frappe.flags.current_date
		try:
			pe.insert()
			pe.submit()
			frappe.db.commit()
			outstanding_invoices.remove(inv)
		except erpnext.accounts.utils.FiscalYearError:
			add_fiscal_year(frappe.flags.current_date)

	# make payment via JV
	for inv in outstanding_invoices[:1]:
		jv = frappe.get_doc(get_payment_entry_against_invoice(ref_doctype, inv.name))
		jv.posting_date = frappe.flags.current_date
		jv.cheque_no = random_string(6)
		jv.cheque_date = frappe.flags.current_date
		try:
			jv.insert()
			jv.submit()
			frappe.db.commit()
		except erpnext.accounts.utils.FiscalYearError:
			add_fiscal_year(frappe.flags.current_date)

def add_fiscal_year(date):
	fy = frappe.new_doc("Fiscal Year")
	fy.year = getdate(date).year
	fy.year_start_date = getdate(date).replace(day=1, month=1)
	fy.year_end_date = getdate(date).replace(day=31, month=12)
	fy.insert()
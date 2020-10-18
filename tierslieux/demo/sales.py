# Copyright (c) 2020, Dokos SAS and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals

import frappe, random, erpnext
from frappe import _
from frappe.utils import flt
from frappe.utils.make_random import add_random_children, get_random
from erpnext.setup.utils import get_exchange_rate
from erpnext.accounts.party import get_party_account_currency
from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request, make_payment_entry

def run():
	frappe.set_user("thierry@dokos.io")
	frappe.set_user_lang("fr")

	for i in range(random.randint(1,7)):
		if random.random() < 0.5:
			make_opportunity()

	for i in range(random.randint(1,7)):
		if random.random() < 0.5:
			make_quotation()

	try:
		lost_reason = frappe.get_doc({
			"doctype": "Opportunity Lost Reason",
			"lost_reason": _("Did not ask")
		})
		lost_reason.save(ignore_permissions=True)
	except frappe.exceptions.DuplicateEntryError:
		pass

	# lost quotations / inquiries
	if random.random() < 0.3:
		for i in range(random.randint(1,3)):
			quotation = get_random('Quotation', doc=True)
			if quotation and quotation.status == 'Submitted':
				quotation.declare_order_lost([{'lost_reason': _('Did not ask')}])

		for i in range(random.randint(1,3)):
			opportunity = get_random('Opportunity', doc=True)
			if opportunity and opportunity.status in ('Open', 'Replied'):
				opportunity.declare_enquiry_lost([{'lost_reason': _('Did not ask')}])

	for i in range(random.randint(1,7)):
		if random.random() < 0.6:
			make_sales_order()

	if random.random() < 0.5:
		#make payment request against Sales Order
		sales_order_name = get_random("Sales Order", filters={"docstatus": 1})
		try:
			if sales_order_name:
				so = frappe.get_doc("Sales Order", sales_order_name)
				if flt(so.per_billed) != 100:
					payment_request = make_payment_request(dt="Sales Order", dn=so.name, recipient_id=so.contact_email,
						submit_doc=True, mute_email=True, use_dummy_message=True)

					payment_entry = frappe.get_doc(make_payment_entry(payment_request.name))
					payment_entry.posting_date = frappe.flags.current_date
					payment_entry.submit()
		except Exception:
			pass

def make_opportunity():
	b = frappe.get_doc({
		"doctype": "Opportunity",
		"opportunity_from": "Customer",
		"party_name": frappe.get_value("Customer", get_random("Customer", filters={"name": ("!=", "Guest")}), 'name'),
		"opportunity_type": _("Sales"),
		"with_items": 1,
		"transaction_date": frappe.flags.current_date,
	})

	add_random_children(b, "items", rows=2, randomize = {
		"qty": (1, 5),
		"item_code": ("Item", {"has_variants": 0, "is_fixed_asset": 0, "is_down_payment_item": 0, "is_sales_item": 1})
	}, unique="item_code")

	b.insert(ignore_permissions=True)
	frappe.db.commit()

def make_quotation():
	# get open opportunites
	opportunity = get_random("Opportunity", {"status": "Open", "with_items": 1})

	if opportunity:
		from erpnext.crm.doctype.opportunity.opportunity import make_quotation
		qtn = frappe.get_doc(make_quotation(opportunity))
		qtn.transaction_date = frappe.flags.current_date
		qtn.order_type = "Sales"
		qtn.insert(ignore_permissions=True)
		frappe.db.commit()
		qtn.submit()
		frappe.db.commit()
	else:
		# make new directly

		# get customer, currency and exchange_rate
		customer = get_random("Customer", filters={"name": ("!=", "Guest")})

		company_currency = frappe.get_cached_value('Company',  erpnext.get_default_company(),  "default_currency")
		party_account_currency = get_party_account_currency("Customer", customer, erpnext.get_default_company())
		if company_currency == party_account_currency:
			exchange_rate = 1
		else:
			exchange_rate = get_exchange_rate(party_account_currency, company_currency, args="for_selling")

		qtn = frappe.get_doc({
			"creation": frappe.flags.current_date,
			"doctype": "Quotation",
			"quotation_to": "Customer",
			"party_name": customer,
			"currency": party_account_currency or company_currency,
			"conversion_rate": exchange_rate,
			"order_type": "Sales",
			"transaction_date": frappe.flags.current_date,
		})

		add_random_children(qtn, "items", rows=3, randomize = {
			"qty": (1, 5),
			"item_code": ("Item", {"has_variants": "0", "is_fixed_asset": 0, "is_down_payment_item": 0, "is_sales_item": 1})
		}, unique="item_code")

		qtn.insert(ignore_permissions=True)
		frappe.db.commit()
		qtn.submit()
		frappe.db.commit()

def make_sales_order():
	q = get_random("Quotation", {"docstatus": 1, "status": "Open"})
	if q:
		from erpnext.selling.doctype.quotation.quotation import make_sales_order as mso
		so = frappe.get_doc(mso(q))
		so.transaction_date = frappe.flags.current_date
		so.delivery_date = frappe.utils.add_days(frappe.flags.current_date, 10)
		so.payment_schedule = []
		so.insert(ignore_permissions=True)
		frappe.db.commit()
		so.submit()
		frappe.db.commit()

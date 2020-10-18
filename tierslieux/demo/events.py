# Copyright (c) 2020, Dokos SAS and Contributors
# License: GNU General Public License v3. See license.txt

import frappe, random, erpnext
from frappe import _
from frappe.utils import flt, add_days
from frappe.utils.make_random import get_random
from erpnext.venue.doctype.item_booking.item_booking import get_availabilities

def run():
	frappe.set_user("thierry@dokos.io")
	frappe.set_user_lang("fr")

	for i in range(random.randint(1,7)):
		if random.random() < 0.5:
			make_event()

def make_event():
	pass
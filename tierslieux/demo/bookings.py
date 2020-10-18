# Copyright (c) 2020, Dokos SAS and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals

import frappe, random, erpnext
from frappe import _
from frappe.utils import flt, add_days
from frappe.utils.make_random import get_random
from erpnext.venue.doctype.item_booking.item_booking import get_availabilities

STATUSES = ["Confirmed", "Not confirmed", "Cancelled"]

def run():
	frappe.set_user("thierry@dokos.io")
	frappe.set_user_lang("fr")

	for i in range(random.randint(1,7)):
		if random.random() < 0.5:
			make_item_booking()

def make_item_booking():
	user = get_random("User")
	item = get_random("Item", filters={"enable_item_booking": 1})

	frappe.set_user(user)
	frappe.set_user_lang("fr")

	availabilities = get_availabilities(item, add_days(frappe.flags.current_date, 1), add_days(frappe.flags.current_date, 2))
	if availabilities:
		availability = availabilities[random.randint(0, len(availabilities) - 1)]

		ib = frappe.get_doc({
			"doctype": "Item Booking",
			"user": user,
			"item": item,
			"starts_on": availability.get("start"),
			"ends_on": availability.get("end"),
			"status": STATUSES[random.randint(0, 2)]
		})

		ib.insert(ignore_permissions=True)
		frappe.db.commit()
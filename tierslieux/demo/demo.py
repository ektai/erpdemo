import frappe
import json
import erpnext
import sys
from frappe.utils import cint, getdate, today
import random
from frappe.utils.password import update_password

from tierslieux.demo  import sales, projects, accounts, purchases, bookings
from erpnext.stock.doctype.item_price.item_price import ItemPriceDuplicateItem

def configure_demo(days=100, resume=False):
	frappe.flags.in_demo = 1

	if not resume:
		setup_site()

		if frappe.conf.stripe_public_key and frappe.conf.stripe_secret_key:
			setup_stripe()

		if frappe.conf.gocardless_token:
			setup_gocardless()

		setup_cart()

	site = frappe.local.site
	frappe.destroy()
	frappe.init(site)
	frappe.connect()

	simulate(days)

def simulate(days=100):
	print("Running Simulation...")
	runs_for = frappe.flags.runs_for or days
	frappe.flags.company = erpnext.get_default_company()
	frappe.flags.mute_emails = True

	if not frappe.flags.start_date:
		# start date = 100 days back
		frappe.flags.start_date = frappe.utils.add_days(frappe.utils.nowdate(),
			-1 * runs_for)

	current_date = frappe.utils.getdate(frappe.flags.start_date)

	# continue?
	demo_last_date = frappe.db.get_global('demo_last_date')
	if demo_last_date:
		current_date = frappe.utils.add_days(frappe.utils.getdate(demo_last_date), 1)

	# run till today
	if not runs_for:
		runs_for = frappe.utils.date_diff(frappe.utils.nowdate(), current_date)
		# runs_for = 100

	for i in range(runs_for):
		sys.stdout.write("\rSimulating {0}: Day {1}".format(
			current_date.strftime("%Y-%m-%d"), i))
		sys.stdout.flush()
		frappe.flags.current_date = current_date
		if current_date.weekday() in (5, 6):
			current_date = frappe.utils.add_days(current_date, 1)
			continue
		try:
			projects.run_projects(current_date)
			sales.run()
			# TODO: Add purchases with inventory items
			#purchases.run()
			accounts.run()
			bookings.run()

		except:
			frappe.db.set_global('demo_last_date', current_date)
			raise
		finally:
			current_date = frappe.utils.add_days(current_date, 1)
			frappe.db.commit()

def setup_site():
	initalize_site()
	setup_website()
	setup_items()
	setup_item_bookings()
	setup_users()
	setup_employees()
	setup_holiday_lists()
	setup_knowledge_base()
	setup_portal()
	setup_customers()
	setup_suppliers()
	setup_subscriptions()
	clear_onboarding()
	frappe.db.commit()

def initalize_site():
	print("Initialization...")
	from frappe.desk.page.setup_wizard.setup_wizard import setup_complete
	if not frappe.get_all('Company', limit=1):
		completed = setup_complete({
			"full_name": "Thierry Lussier",
			"email": "thierry@dokos.io",
			"company_tagline": 'Mon Tiers Lieux',
			"password": "tierslieux",
			"fy_start_date": "2020-01-01",
			"fy_end_date": "2020-12-31",
			"bank_account": "Banque Nationale",
			"domains": ["Venue"],
			"company_name": "Mon Tiers Lieux",
			"chart_of_accounts": "Plan Comptable Général",
			"company_abbr": "MTL",
			"currency": 'EUR',
			"timezone": 'Europe/Paris',
			"country": 'France',
			"language": "Français",
			"lang": "fr",
			"demo": 1
		})
		print(completed)

def setup_website():
	print("Website Setup...")
	colors = json.loads(open(frappe.get_app_path('tierslieux', 'data', 'colors.json')).read())
	for color in colors:
		doc = frappe.get_doc(color)
		try:
			doc.insert()
		except frappe.DuplicateEntryError:
			continue

	for filename in ["accueil", "website_theme", "website_settings"]:
		data = json.loads(open(frappe.get_app_path('tierslieux', 'data', f'{filename}.json')).read())
		doc = frappe.get_doc(data)
		try:
			doc.insert()
		except frappe.DuplicateEntryError:
			continue

	theme = frappe.get_doc("Website Theme", "Thème Personnalisé")
	theme.custom_overrides = "$navbar-height: 6rem;"
	theme.custom_scss = open(frappe.get_app_path('tierslieux', 'public', 'scss', 'website_theme.scss')).read()
	theme.save()

def setup_items():
	print("Items Setup...")

	for filename in ["item_groups", "items", "prices"]:
		data = json.loads(open(frappe.get_app_path('tierslieux', 'data', f'{filename}.json')).read())
		for item in data:
			doc = frappe.get_doc(item)
			try:
				doc.insert()
			except frappe.DuplicateEntryError:
				continue
			except ItemPriceDuplicateItem:
					continue
		frappe.db.commit()

	venue_settings = frappe.get_single("Venue Settings")
	venue_settings.item_group = "Coworking"
	venue_settings.stock_uom = "Unité"
	venue_settings.minute_uom = "Minute"
	venue_settings.save()

def setup_cart():
	print("Cart Setup...")
	cart_settings = frappe.get_single("Shopping Cart Settings")
	cart_settings.enabled = 1
	cart_settings.show_price = 1
	cart_settings.show_contact_us_button = 0
	cart_settings.allow_item_not_in_stock = 1

	if frappe.get_all("Stripe Settings"):
		cart_settings.enable_checkout = 1
		cart_settings.payment_gateway_account = "Stripe-Stripe - EUR"
		cart_settings.payment_success_url = "Invoices"

	cart_settings.save()
	frappe.db.commit()

def setup_users():
	print("Users Setup...")

	frappe.get_doc("User", "thierry@dokos.io").hide_modules()

	try:
		portal_user = frappe.get_doc({
			"email": "francis@dokos.io",
			"first_name": "Francis",
			"last_name": "Charpentier",
			"language": "fr",
			"doctype": "User",
			"send_welcome_email": 0
		})
		portal_user.insert()
		portal_user.add_roles("Customer")
		portal_user.add_roles("Volunteer")
		update_password(portal_user.name, "tierslieux")
	except frappe.DuplicateEntryError:
		pass

	employees = [
		{
			"email": "tilly@dokos.io",
			"first_name": "Tilly",
			"last_name": "LaCaille",
			"language": "fr",
			"doctype": "User",
			"send_welcome_email": 0,
			"new_password": "tierslieux"
		},
		{
			"email": "alfred@dokos.io",
			"first_name": "Alfred",
			"last_name": "Faubert",
			"language": "fr",
			"doctype": "User",
			"send_welcome_email": 0,
			"new_password": "tierslieux"
		},
		{
			"email": "huette@dokos.io",
			"first_name": "Huette",
			"last_name": "Fortier",
			"language": "fr",
			"doctype": "User",
			"send_welcome_email": 0,
			"new_password": "tierslieux"
		},
		{
			"email": "agnes@dokos.io",
			"first_name": "Agnès",
			"last_name": "Pomerleau",
			"language": "fr",
			"doctype": "User",
			"send_welcome_email": 0,
			"new_password": "tierslieux"
		}
	]
	for employee in employees:
		try:
			user = frappe.get_doc(employee)
			user.insert()
			user.add_roles("Employee")
			update_password(user.name, "tierslieux")
		except frappe.DuplicateEntryError:
			continue

	frappe.db.commit()

def setup_employees():
	load_file("employees")

	default_leave_policy = frappe.get_all("Leave Policy")
	if default_leave_policy:
		for employee in frappe.get_all("Employee"):
			frappe.db.set_value("Employee", employee.name, "leave_policy", default_leave_policy[0].name)

def setup_holiday_lists():
	from erpnext.regional.france.hr.bank_holidays import get_french_bank_holidays
	holiday_lists = [
		{
			"holiday_list_name": "2019",
			"from_date": "2019-01-01",
			"to_date": "2019-12-31",
			"doctype": "Holiday List"
		},
		{
			"holiday_list_name": "2020",
			"from_date": "2020-01-01",
			"to_date": "2020-12-31",
			"doctype": "Holiday List"
		},
		{
			"holiday_list_name": "2021",
			"from_date": "2021-01-01",
			"to_date": "2021-12-31",
			"doctype": "Holiday List",
			"replaces_holiday_list": "2020"
		}
	]

	for hl in holiday_lists:
		try:
			holiday_list = frappe.get_doc(hl)
			holiday_list.insert()
			french_bh = get_french_bank_holidays(cint(holiday_list.holiday_list_name))

			for bank_holiday in french_bh:
				holiday_list.append("holidays", {
					"holiday_date": french_bh[bank_holiday],
					"description": bank_holiday
				})

			for off_day in ["Saturday", "Sunday"]:
				holiday_list.weekly_off = off_day
				holiday_list.get_weekly_off_dates()
			holiday_list.save()

		except frappe.DuplicateEntryError:
			pass

	frappe.db.set_value("Company", "Mon Tiers Lieux", "default_holiday_list", "2020")

def setup_attendance():
	from erpnext.hr.doctype.holiday_list.holiday_list import is_holiday
	import pandas as pd

	for employee in frappe.get_all("Employee"):
		for date in pd.date_range(start="2019-01-01",end=getdate(today())):
			doc = {
					"doctype": "Attendance",
					"employee": employee.name,
					"attendance_date": date.date(),
				}
			if is_holiday(str(date.year), date):
				doc["status"] = "Absent"
			elif random.random() < 0.05:
				doc["status"] = "On Leave"
				doc["leave_type"] = "Congés payés" if random.random() < 0.7 else "RTT"
			else:
				doc["status"] = "Present"

			try:
				inserted_doc = frappe.get_doc(doc).insert()
				inserted_doc.submit()
			except frappe.ValidationError as e:
				continue

def setup_knowledge_base():
	print("Knowledge Base Setup...")
	kb_articles = json.loads(open(frappe.get_app_path('tierslieux', 'data', 'help.json')).read())
	for article in kb_articles:
		doc = frappe.get_doc(article)
		try:
			doc.insert()
		except frappe.DuplicateEntryError:
			continue
	frappe.db.commit()

def setup_portal():
	print("Portal Setup...")
	portal_settings = frappe.get_single("Portal Settings")
	portal_settings.hide_standard_menu = 1
	for menu in [
		{
			"title": "Aide",
			"enabled": 1,
			"route": "/kb/informations-pratiques",
			"reference_doctype": "Help Article",
			"role": "Customer",
		},
		{
			"title": "Support",
			"enabled": 1,
			"route": "/issues",
			"reference_doctype": "Issue",
			"role": "Customer",
		},
		{
			"title": "Evènements",
			"enabled": 1,
			"route": "/events",
			"reference_doctype": "Event",
			"role": "Customer",
		},
		{
			"title": "Inscriptions aux événements",
			"enabled": 1,
			"route": "/event-slots",
			"reference_doctype": "Event Slot Booking",
			"role": "Volunteer",
		},
		{
			"title": "Réservations",
			"enabled": 1,
			"route": "/bookings",
			"reference_doctype": "Item Booking",
			"role": "Customer",
		},
		{
			"title": "Commandes",
			"enabled": 1,
			"route": "/orders",
			"reference_doctype": "Sales Order",
			"role": "Customer",
		},
		{
			"title": "Factures",
			"enabled": 1,
			"route": "/invoices",
			"reference_doctype": "Sales Invoice",
			"role": "Customer",
		},
		{
			"title": "Documents Personnels",
			"enabled": 1,
			"route": "/document-personnel",
			"reference_doctype": "Document Personnel",
			"role": "Customer",
		},
		{
			"title": "Abonnement",
			"enabled": 1,
			"route": "/subscription",
			"role": "Customer",
		}
		
	]:
		portal_settings.append("custom_menu", menu)
	portal_settings.save()

def setup_item_bookings():
	print("Item Booking Setup...")
	booking_calendars = json.loads(open(frappe.get_app_path('tierslieux', 'data', 'booking_calendars.json')).read())
	for calendar in booking_calendars:
		doc = frappe.get_doc(calendar)
		try:
			doc.insert()
		except frappe.DuplicateEntryError:
			continue

	uom = frappe.get_doc({
		"doctype": "UOM Conversion Factor",
		"category": "Temps",
		"from_uom": "Demi-journée",
		"to_uom": "Minute",
		"value": "300"
	})
	try:
		uom.insert()
	except frappe.DuplicateEntryError:
		pass

	doc = frappe.get_doc("UOM Conversion Factor", {"from_uom": "Jour", "to_uom": "Minute"})
	doc.value = 700
	doc.save()

	frappe.db.commit()

def setup_customers():
	print("Customers Setup...")
	for filename in ["customers", "customers_contacts", "customers_addresses"]:
		load_file(filename)

def setup_suppliers():
	print("Suppliers Setup...")
	for filename in ["suppliers", "suppliers_contacts", "suppliers_addresses"]:
		load_file(filename)

def setup_subscriptions():
	print("Subscription Setup...")
	for filename in ["subscription_plans", "subscription_templates"]:
		load_file(filename)

def clear_onboarding():
	print("Clearing Onboarding...")
	for doc in frappe.get_all("Module Onboarding"):
		frappe.db.set_value("Module Onboarding", doc.name, "is_complete", 1)


def setup_stripe():
	print("Stripe Setup...")
	stripe_account = frappe.get_doc({
		"doctype": "Stripe Settings",
		"gateway_name": "Stripe",
		"secret_key": frappe.conf.stripe_secret_key,
		"publishable_key": frappe.conf.stripe_public_key,
		"webhook_secret_key": frappe.conf.stripe_webhook_key,
		"bank_account": "Banque Nationale - Banque Nationale"
	})

	try:
		stripe_account.insert()
	except frappe.DuplicateEntryError:
		pass

	gateway = frappe.get_doc("Payment Gateway", "Stripe-Stripe")
	gateway.mode_of_payment = "Carte de Crédit"
	gateway.fee_account = "627 - Services bancaires et assimilés - MTL"
	gateway.cost_center = "Principal - MTL"
	gateway.title = "Carte bancaire"
	gateway.save()

	frappe.get_doc({
		"doctype": "Account",
		"account_name": "Stripe-USD",
		"account_number": 512410,
		"account_currency": "USD",
		"parent_account": "512 - Banques - MTL"
	}).insert()
	frappe.db.commit()

	frappe.get_doc({
		"doctype": "Payment Gateway Account",
		"payment_gateway": "Stripe-Stripe",
		"payment_account": "512410 - Stripe-USD - MTL",
		"currency": "USD",
		"parent_account": "512 - Banques - MTL"
	}).insert()
	frappe.db.commit()

def setup_gocardless():
	print("GoCardless Setup...")
	gocardless_account = frappe.get_doc({
		"doctype": "GoCardless Settings",
		"gateway_name": "GoCardless",
		"access_token": frappe.conf.gocardless_token,
		"webhooks_secret": frappe.conf.gocardless_webhook_key,
		"use_sandbox": 1
	})

	try:
		gocardless_account.insert()
	except frappe.DuplicateEntryError:
		pass

	gateway = frappe.get_doc("Payment Gateway", "GoCardless-GoCardless")
	gateway.mode_of_payment = "Virement"
	gateway.fee_account = "627 - Services bancaires et assimilés - MTL"
	gateway.cost_center = "Principal - MTL"
	gateway.title = "Prélèvement SEPA"
	gateway.icon = "Wire Transfer"
	gateway.save()
	frappe.db.commit()

def load_file(filename):
	data = json.loads(open(frappe.get_app_path('tierslieux', 'data', f'{filename}.json')).read())
	for item in data:
		doc = frappe.get_doc(item)
		try:
			doc.insert()
		except frappe.DuplicateEntryError:
			continue
	frappe.db.commit()
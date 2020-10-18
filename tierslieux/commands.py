# Copyright (c) 2020, Dokos SAS and Contributors
# See license.txt

import click
import frappe
from frappe.commands import pass_context, get_site
import json

@click.command('demo-tierslieux')
@click.option('--reinstall', default=False, is_flag=True, help='Reinstall site before demo')
@click.option('--days', default=100, help='Run the demo for so many days. Default 100')
@click.option('--resume', default=False, is_flag=True, help='Generate additional demo days')
@click.option('--admin-password', help='Administrator Password for reinstalled site')
@click.option('--mariadb-root-username', help='Root username for MariaDB')
@click.option('--mariadb-root-password', help='Root password for MariaDB')
@click.option('--site', help='site name')
@pass_context
def demo_tierslieux(context, domain='Manufacturing', reinstall=False, days=100, resume=False, admin_password=None,
	mariadb_root_username=None, mariadb_root_password=None, site=None):
	"Reinstall site and setup a demo for Tiers Lieux"
	from frappe.commands.site import _reinstall
	from frappe.installer import install_app

	if not site:
		site = get_site(context)

	if reinstall:
		_reinstall(site=site, admin_password=admin_password, mariadb_root_username=mariadb_root_username, mariadb_root_password=mariadb_root_password, yes=True)

	with frappe.init_site(site=site):
		frappe.connect()
		for app in ("erpnext", "tierslieux"):
			if app not in frappe.get_installed_apps():
				install_app(app)

		# import needs site
		from tierslieux.demo.demo import configure_demo
		configure_demo(days, resume)

commands = [
	demo_tierslieux
]
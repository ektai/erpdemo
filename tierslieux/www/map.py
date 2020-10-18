# Copyright (c) 2020, Dokos SAS and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe

sitemap = 1

def get_context(context):
	context.full_width = True
	context.navbar_search = False
	return context
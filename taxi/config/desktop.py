# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "Taxi",
			"color": "grey",
			"icon": "octicon octicon-location",
			"type": "module",
			"label": _("Taxi")
		},
                {
                        "module_name": "Trip Order",
                        "color": "#c0392b",
                        "icon": "octicon octicon-tag",
                        "label": _("Trip Order"),
                        "link": "List/Trip Order",
                        "_doctype": "Trip Order",
                        "type": "list",
                        "hidden": 0
                }

	]

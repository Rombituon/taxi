from __future__ import unicode_literals
from frappe import _

def get_data():
        return [
                {
                        "label": _("Trips Management"),
                        "items": [
                                {
                                        "type": "doctype",
                                        "name": "Trip Order",
                                        "description": _("Trip Order."),
                                },
                                {
                                        "type": "doctype",
                                        "name": "Taxi Subscription",
                                        "description": _("Taxi Subscription"),
                                },
                                {
                                        "type": "doctype",
                                        "name": "Type Of Service",
                                        "description": _("Type Of Service"),
                                },
                                {
                                        "type": "doctype",
                                        "name": "Route Pricing Settings",
                                        "description": _("Route Pricing Settings"),
                                }
			]
		},
		{
                        "label": _("Taxi Fleet Management"),
                        "items": [
                                {
                                        "type": "doctype",
                                        "name": "Vehicle",
#                                        "description": _("Taxi Vehicle"),
                                        "label": _("Taxi Vehicle"),
                                },
                                {
                                        "type": "doctype",
                                        "name": "Vehicle Log",
#                                        "description": _("Taxi Vehicle Log"),
                                        "label": _("Taxi Vehicle Log"),
                                }
                        ]
		},
                {
                        "label": _("Drivers Management"),
                        "items": [
                                {
                                        "type": "doctype",
                                        "name": "Drivers",
                                        "description": _("Drivers"),
                                },
                                {
                                        "type": "doctype",
                                        "name": "Clearance With Driver",
                                        "description": _("Clearance With Driver"),
                                },
				{	                                        
					"type": "doctype",
                                        "name": "Commission Rule",
                                        "description": _("Commission Rule"),
				},
                                {
                                        "type": "doctype",
                                        "name": "Assign Commission Rule",
                                        "description": _("Assign Commission Rule"),
                                },
                                {
                                        "type": "doctype",
                                        "name": "Test Driver",
                                        "description": _("Test Driver"),
				}
                        ]
                }
	]

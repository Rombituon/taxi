from frappe import _

def get_data():
	return {
		'fieldname': 'trip_order',
		'transactions': [
			{
				'label': _('Fulfillment'),
				'items': ['Sales Invoice', 'Delivery Note']
			},
			{
				'label': _('Purchasing'),
				'items': ['Material Request', 'Purchase Order']
			},
			{
				'label': _('Projects'),
				'items': ['Project']
			},
			{
				'label': _('Manufacturing'),
				'items': ['Production Order']
			},
			{
				'label': _('Reference'),
				'items': ['Quotation', 'Subscription']
			},
			{
				'label': _('Payment'),
				'items': ['Payment Entry', 'Payment Request', 'Journal Entry']
			},
		]
	}

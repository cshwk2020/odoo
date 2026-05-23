{
    'name': 'Sale Order Notification',
    'version': '19.0.1.0.0',
    'depends': ['sale','web'],
    'category': 'Sales/Sale Order Notification',
    'sequence': 3,
    'data': [
        'views/sale_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [

            #'sale_notification/static/src/js/notification_listener.js',
        ],
    },

    'installable': True,
    'application': True,
}

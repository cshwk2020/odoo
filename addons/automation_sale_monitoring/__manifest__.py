{
    'name': 'Automation Sale Monitoring',
    'version': '1.0',
    'depends': ['base', 'sale_management', 'mail'],
    'category': 'Sales',
    'sequence': 5,
    'data': [
        'security/ir.model.access.csv',
        'views/sale_monitoring_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'automation_sale_monitoring/static/src/css/style.css',
        ],
    },
    'installable': True,
    'application': True,
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}

{
    'name': 'Automation Dashboard',
    'version': '1.0',
    'depends': ['base', 'account', 'hr_expense'],
    'category': 'Automation',
    'sequence': 2,
    'data': [
        'security/ir.model.access.csv',
        'views/automation_monitoring_views.xml',

    ],
    "assets": {
        "web.assets_backend": [
            "automation_dashboard/static/src/js/open_ref_modal.js",
        ],
    },
    'installable': True,
    'application': True,
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}

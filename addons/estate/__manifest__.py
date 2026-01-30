{
    'name': 'Estate',
    'version': '1.0',
    'depends': ['base'],
    'category': 'Estate',
    'sequence': 2,
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_tag_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_views.xml',
    ],
    'installable': True,
    'application': True,
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}

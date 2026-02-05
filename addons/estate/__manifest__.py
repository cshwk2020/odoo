{
    'name': 'Estate',
    'version': '1.0',
    'depends': ['base', 'account'],
    'category': 'Estate',
    'sequence': 2,
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_tag_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_views.xml',
        'views/estate_property_offer_form.xml',
        'views/users_form_inherit_estate_views.xml',
    ],
    'installable': True,
    'application': True,
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}

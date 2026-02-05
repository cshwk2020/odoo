{
    'name': 'Estate Account',
    'version': '1.0',
    'summary': 'Link module between Estate and Accounting',
    'description': """ 
        This module links the Estate module with the Accounting module. 
        When both are installed, it will allow invoice creation from estate properties. 
        """,
    'depends': ['estate', 'account'],
    'category': 'Estate',
    'sequence': 3,
    'data': [
        'security/ir.model.access.csv',

    ],
    'installable': True,
    'application': True,
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}

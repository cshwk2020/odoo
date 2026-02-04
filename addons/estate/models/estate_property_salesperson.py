from odoo import models, fields

class EstatePropertySalesperson(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many(
        'estate.property',        # target model
        'salesperson_id',         # inverse field in estate.property
        string="Properties",
        domain=[('state', 'in', 'available')]  # only available properties
    )




from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"

    name = fields.Char(string="Name", required=True)

    # Property type name must be unique
    _unique_property_type_name = models.Constraint(
        'UNIQUE(name)',
        'The name of a property type must be unique.',
    )


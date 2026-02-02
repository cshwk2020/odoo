from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag"
    _order = "name"
    name = fields.Char(string="Name", required=True)

    # Property tag name must be unique
    _unique_property_tag_name = models.Constraint(
        'UNIQUE(name)',
        'The name of a property tag must be unique.',
    )




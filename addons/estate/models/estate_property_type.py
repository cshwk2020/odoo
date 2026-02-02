from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"
    _order = "sequence, name"

    sequence = fields.Integer(string="Sequence", default=10)

    name = fields.Char(string="Name", required=True)

    property_ids = fields.One2many( "estate.property",
                                    "property_type_id",
                                    string="Properties" )

    property_names = fields.Char(
        string="Property Names",
        compute="_compute_property_names" )

    def _compute_property_names(self):
        for record in self:
            record.property_names = ", ".join(record.property_ids.mapped("name"))


    # Property type name must be unique
    _unique_property_type_name = models.Constraint(
        'UNIQUE(name)',
        'The name of a property type must be unique.',
    )


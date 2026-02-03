from odoo import api, models, fields

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

    #
    offer_ids = fields.One2many( "estate.property.offer",
                                 "property_type_id",
                                 string="Offers" )

    offer_count = fields.Integer( string="Offer Count",
                                  compute="_compute_offer_count" )

    offer_count_label = fields.Char( string="Offers",
                                     compute="_compute_offer_count_label" )

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = str(len(record.offer_ids)  )


    @api.depends("offer_ids")
    def _compute_offer_count_label(self):
        for record in self:
            record.offer_count_label = f"Offers ({len(record.offer_ids)})"

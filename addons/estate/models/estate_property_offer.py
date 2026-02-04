from odoo import models, fields, api
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = "price desc"


    # offer price
    price = fields.Float(string="Price")
    _check_offer_price = models.Constraint(
        'CHECK(price > 0)',
        'The property offer price must be strictly positive.',
    )

    property_type_id = fields.Many2one( "estate.property.type",
                                        string="Property Type",
                                        related="property_id.property_type_id",
                                        store=True, )

    status = fields.Selection(
        [
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        string="Status",
        copy=False
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Buyer",
        required=True
    )

    property_id = fields.Many2one(
        "estate.property",
        string="Property",
        required=True
    )

    def action_accept(self):
        for offer in self:
            if offer.property_id.state == 'sold':
                raise UserError("This property is already sold.")

            elif offer.property_id.state == 'cancelled':
                raise UserError("This property is already cancelled.")

            # ensure only one accepted offer per property
            if offer.property_id.offer_ids.filtered(lambda o: o.status == 'accepted'):
                raise UserError("Only one offer can be accepted for a property.")
            offer.status = 'accepted'
            offer.property_id.write({
                'partner_id': offer.partner_id.id,
                'selling_price': offer.price,
                'state': 'sold',
            })
        return True

    def action_refuse(self):
        for offer in self:
            if offer.property_id.state == 'sold':
                raise UserError("This property is already sold.")

            offer.status = 'refused'
        return True



    @api.model
    def create(self, vals_list): # vals is new db row constructing in progress, not yet insert to db yet

        for vals in vals_list:
            property = self.env['estate.property'].browse(vals['property_id'])

            # Check if offer amount is lower than existing offers
            if property.offer_ids and vals.get('price'):
                max_offer = max(property.offer_ids.mapped('price'))
                if vals['price'] < max_offer:
                    raise UserError("Offer must be higher than existing offers.")

            # Update property state
            property.state = 'offer_received'

        return super().create(vals_list)

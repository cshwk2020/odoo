import sys
from datetime import timedelta
from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Test Model"
    _order = "id desc"


    #
    total_area = fields.Float( compute="_compute_total_area", store=True )

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area



    #
    property_type_id = fields.Many2one(
        "estate.property.type",
        string="Property Type"
    )



    partner_id = fields.Many2one( "res.partner",
                              string="Partner",
                              ondelete="set null",
                              copy=False)

    @api.onchange("partner_id")
    def _onchange_partner_id(self):

        if self.partner_id  and self.partner_id.name:
            self.name = "Document for %s" % (self.partner_id.name)
        else:
            self.name = "New Document"


        self.description = "Default description for %s" % (self.partner_id.name)


    salesperson_id = fields.Many2one("res.users",
                              string="Salesperson",
                              default=lambda self: self.env.user)


    tag_ids = fields.Many2many( "estate.property.tag", string="Tags" )

    offer_ids = fields.One2many(
        "estate.property.offer",
        "property_id",
        string="Offers",
    )


    # at_uninstall=True → run your deletion checks even during uninstall.
    # at_uninstall=False → skip your deletion checks during uninstall, so the module can be removed cleanly
    @api.ondelete(at_uninstall=False)
    def _unlink_if_allowed(self):
        for record in self:
            if record.state not in ('new', 'cancelled'):
                raise UserError(
                    "You can only delete properties in state 'New' or 'Cancelled'."
                )



    #
    name = fields.Char(string="Name")
    # description = fields.Text(string="Description")
    description = fields.Char(
        compute="_compute_description",
        store=True)
    @api.depends("partner_id.name")
    def _compute_description(self):
        for record in self:
            if record.partner_id and record.partner_id.name:
                record.description = "Test for partner %s" % record.partner_id.name
            else:
                record.description = "Test for partner"



    best_price = fields.Float( string="Best Offer",
                               compute="_compute_best_price",
                               store=True )

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            prices = record.offer_ids.mapped("price")
            record.best_price = max(prices) if prices else float(-sys.maxsize)


    #
    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("A sold property cannot be cancelled.")
            elif record.state == 'cancelled':
                raise UserError("property already cancelled.")

            record.state = 'cancelled'
        return True

    def action_sold(self):
        for record in self:
            if record.state == 'cancelled':
                raise UserError("A cancelled property cannot be sold.")
            elif record.state == 'sold':
                raise UserError("property already sold.")

            record.state = 'sold'
        return True




    postcode = fields.Char(string="Postcode")

    date_availability = fields.Date(
        string="Date Availability",
        default=lambda self: fields.Date.today() + timedelta(days=90),
        copy=False
    )
    expected_price = fields.Float(string="Expected Price")
    selling_price = fields.Float(
        string="Selling Price",
        readonly=True,
        copy=False
    )

 


    bedrooms = fields.Integer(
        string="Bedrooms",
        default=2
    )

    #living_area = fields.Integer(string="Living Area")
    living_area = fields.Integer(string="Living Area", store=True, index=True)

    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")

    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area")
    garden_orientation = fields.Selection(
        [
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ],
        string="Garden Orientation"
    )

    # Reserved fields
    active = fields.Boolean(string="Active", default=True)
    state = fields.Selection(
        [ ("new", "New"),
          ("offer_received", "Offer Received"),
          ("offer_accepted", "Offer Accepted"),
          ("sold", "Sold"),
          ("cancelled", "Cancelled"), ],
        string="Status",
        default="new" )


    #
    _check_expected_price = models.Constraint(
        'CHECK(expected_price > 0)',
        'The property expected price must be strictly positive.',
    )

    _check_selling_price = models.Constraint(
        'CHECK(selling_price >= 0)',
        'The property selling price must be positive.',
    )

    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        for record in self:
            if record.selling_price and record.selling_price < record.expected_price * 0.9:
                raise ValidationError(
                    "Selling price cannot be lower than 90% of expected price."
                )

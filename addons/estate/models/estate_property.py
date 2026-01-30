from odoo import api, models, fields
from datetime import timedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Test Model"

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


    user_id = fields.Many2one("res.users",
                              string="Salesperson",
                              default=lambda self: self.env.user)

    tag_ids = fields.Many2many( "estate.property.tag", string="Tags" )

    offer_ids = fields.One2many(
        "estate.property.offer",
        "property_id",
        string="Offers",
    )


    #
    name = fields.Char(string="Name")
    # description = fields.Text(string="Description")
    description = fields.Char(compute="_compute_description")
    @api.depends("partner_id.name")
    def _compute_description(self):
        for record in self:
            record.description = "Test for partner %s" % record.partner_id.name

    best_price = fields.Float( string="Best Offer",
                               compute="_compute_best_price",
                               store=True )

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            prices = record.offer_ids.mapped("price")
            record.best_price = max(prices) if prices else float('-inf')





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
    living_area = fields.Integer(string="Living Area")
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


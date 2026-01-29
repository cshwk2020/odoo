from odoo import models, fields
from datetime import timedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Test Model"

    name = fields.Char(string="Name")
    description = fields.Text(string="Description")
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


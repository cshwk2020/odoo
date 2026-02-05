import sys
from datetime import timedelta
from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError

from odoo import models, fields

class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sold(self):

        # Debugging
        print(">>>>>>>>> estate_account: creating invoice for property <<<")

        # Call original logic
        res = super().action_sold()



        # Create a simple invoice::line items as account_move_line
        commission = self.selling_price * 0.06
        admin_fee = 100.00

        move_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.buyer_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [
                (0, 0, {
                    'name': self.name,
                    'quantity': 1,
                    'price_unit': self.selling_price,
                    'tax_ids': [(6, 0, [])],  # <-- no taxes
                }),
                (0, 0, {
                    'name': "Commission (6% of selling price)",
                    'quantity': 1,
                    'price_unit': commission,
                    'tax_ids': [(6, 0, [])],  # no taxes
                }),
                (0, 0, {
                    'name': "Administrative fees",
                    'quantity': 1,
                    'price_unit': admin_fee,
                    'tax_ids': [(6, 0, [])],  # no taxes
                }),

            ],
        }

        invoice = self.env['account.move'].create(move_vals)

        # Link invoice back to property (optional)
        self.invoice_id = invoice.id

        return res

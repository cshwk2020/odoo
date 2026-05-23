from odoo import models, fields, api
from odoo.exceptions import UserError

class ReceiptUploadWizard(models.TransientModel):
    _name = 'receipt.upload.wizard'
    _description = 'Receipt Upload Wizard'

    receipt_image = fields.Binary("Receipt Image", required=True, attachment=True)
    expense_id = fields.Many2one('hr.expense', required=True)

    def action_upload_and_autofill(self):
        """Upload image and trigger autofill"""
        self.ensure_one()

        if not self.receipt_image:
            raise UserError("Please select a receipt image.")

        # Process autofill
        result = self.expense_id.process_autofill_with_image(self.receipt_image)

        # Close wizard
        return {'type': 'ir.actions.act_window_close'}
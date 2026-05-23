from datetime import date
from odoo import models, fields, api
from odoo.exceptions import UserError
import hashlib


class AutomationMonitoring(models.Model):

    _name = "automation.monitoring"
    _description = "Automation Monitoring"

    module = fields.Selection([
        ("expense", "Expense"),
        ("invoice", "Invoice"),
    ], string="Module", required=True)

    #record_date = fields.Date(string="Record Date")
    record_date = fields.Date(
        string="Record Date",
        related="ref_id.date",
        store=False,   # no duplicate storage, always live from hr.expense
        readonly=True
    )

    raw_image = fields.Binary("Raw Image")
    preocr_image = fields.Binary("Preprocessed Image")
    ocr_text = fields.Text("OCR Text")
    ocr_json = fields.Text("OCR JSON")

    status = fields.Selection([
        ("incomplete", "Incomplete"),
        ("complete", "Complete"),
        ("reviewed", "Reviewed"),
        ("error", "Error"),
    ], string="Status", default="incomplete")

    ref_id = fields.Many2one("hr.expense",
                             string="Reference Expense",
                             ondelete="set null")

    ref_url = fields.Char("Reference URL")
    submit_screenshot = fields.Binary("Submit Screenshot")
    confidence = fields.Float("Confidence", digits=(3,2))
    message = fields.Text("Message")
    # image hash for check dupliacate receipt upload
    image_hash = fields.Char("Receipt Image Hash", index=True)
    remark = fields.Text(string="Remark")

    # transient fields for search
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")


    """ 
    @api.model
    def create(self, vals):
        if vals.get("raw_image"):
            # raw_image is base64 in Odoo
            raw_bytes = vals["raw_image"].decode("base64")
            vals["image_hash"] = hashlib.sha256(raw_bytes).hexdigest()
        return super().create(vals)

    def write(self, vals):
        if vals.get("raw_image"):
            raw_bytes = vals["raw_image"].decode("base64")
            vals["image_hash"] = hashlib.sha256(raw_bytes).hexdigest()
        return super().write(vals)
    """


    #
    def _domain_this_month(self):
        today = fields.Date.context_today(self)
        first_day = today.replace(day=1)
        return [('record_date', '>=', first_day), ('record_date', '<=', today)]

    #
    def search(self, domain, offset=0, limit=None, order=None):
        if self.from_date and self.to_date:
            domain += [
                ('record_date', '>=', self.from_date),
                ('record_date', '<=', self.to_date)
            ]
        return super().search(domain, offset=offset, limit=limit, order=order)



    def action_open_ref_modal(self):

        if not self.ref_id or not self.ref_id.exists():
            raise UserError("The linked expense has been deleted or is missing.")

        if (self.module or "").lower() == "expense":
            # open expense record
            return {
                "type": "ir.actions.act_window",
                "res_model": "hr.expense",
                "view_mode": "form",
                "res_id": self.ref_id.id,
                "target": "new",
            }
        elif (self.module or "").lower() == "invoice":
            # open invoice record
            return {
                "type": "ir.actions.act_window",
                "res_model": "account.move",
                "view_mode": "form",
                "res_id": self.ref_id.id,
                "target": "new",
            }
        else:
            return False





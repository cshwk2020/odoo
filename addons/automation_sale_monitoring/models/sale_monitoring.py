import json, ast, base64
import logging
from odoo import models, fields, api
_logger = logging.getLogger(__name__)

class SaleMonitoring(models.Model):
    _name = "sale.monitoring"
    _description = "Sale Monitoring for Initial Emails"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    thread_id = fields.Char("Thread ID")
    email_msg_id = fields.Char("Email Message ID")
    sender_email = fields.Char("Sender Email")
    original_email_message = fields.Text("Original Email Message")
    original_email_body = fields.Text("Original Email Body")

    status = fields.Selection([
        ("pending_reply", "Pending Reply"),
        ("pending_fix", "Pending Fix"),
        ("replied", "Replied"),
    ], default="pending_fix")

    ai_parse_text = fields.Text("AI Parsed Text")
    ai_mmr_json = fields.Text("AI Adjusted JSON")

    # Link 去正式 sale order
    sale_order_id = fields.Many2one("sale.order", string="Linked Sale Order", required=False)

    # Related partner_id，避免 duplicate
    partner_id = fields.Many2one(
        related="sale_order_id.partner_id",
        string="Sender Partner",
        store=False,      # 唔需要存，只係顯示
        readonly=True
    )

    # 直接顯示 sale order line
    order_line_ids = fields.One2many(
        related="sale_order_id.order_line",
        string="Sale Order Lines",
        readonly=True
    )



    # -------------------------------
    # Atomic create: Sale + Monitoring
    # -------------------------------
    @api.model
    def create_order_with_monitoring(self, vals_order, vals_monitoring):
        """Create sale order + monitoring record atomically.
        If sale order fails, rollback monitoring too.
        """
        order = self.env["sale.order"].create(vals_order)



        _logger.critical(f"py_debug...0...: order=={order}")

        vals_monitoring["sale_order_id"] = order.id

        _logger.critical(f"py_debug...10...: vals_monitoring=={vals_monitoring}")
        monitoring = self.create(vals_monitoring)
        _logger.critical(f"py_debug...20...: monitoring=={monitoring}")

        return {
            "order_id": order.id,
            "monitoring_id": monitoring.id,
            "status": True,
        }

    # -------------------------------
    # Monitoring only (no sale order)
    # -------------------------------
    @api.model
    def create_monitoring_only(self, vals_monitoring):
        """Create monitoring record only, sale_order_id left empty."""
        if isinstance(vals_monitoring, list):
            # 如果外部傳咗 list，取第一個 dict
            vals_monitoring = vals_monitoring[0]

        vals_monitoring["sale_order_id"] = False
        _logger.critical(f"py_debug...create_monitoring_only...: vals_monitoring=={vals_monitoring}")

        monitoring = self.create(vals_monitoring)
        return {
            "monitoring_id": monitoring.id,
            "status": True,
            "msg": "Monitoring record created"
        }



    # -----------------------------------------
    # Action: open linked EDIT sale order in modal
    # -----------------------------------------
    def action_open_sale_order_popup(self):
        self.ensure_one()
        if not self.sale_order_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "view_mode": "form",
            "res_id": self.sale_order_id.id,
            "target": "new",   # 🔑 modal popup
        }


    # -------------------------------
    # Odoo side: get or create partner
    # -------------------------------
    @api.model
    def get_or_create_partner(self, sender_email):

        Partner = self.env["res.partner"]
        Category = self.env["res.partner.category"]

        # Step 1: search existing partner
        partner = Partner.search([("email", "=", sender_email)], limit=1)
        if partner:
            return partner

        # Step 2: ensure Public Inquiry category exists
        category = Category.search([("name", "=", "Public Inquiry")], limit=1)
        if not category:
            category = Category.create({"name": "Public Inquiry"})

        # Step 3: create new partner
        partner = Partner.create({
            "name": sender_email.split("@")[0],
            "email": sender_email,
            "customer_rank": 0,
            "category_id": [(4, category.id)],
        })

        return partner


    # -----------------------------------------
    # Action: open linked ADD sale order in modal
    # -----------------------------------------
    def action_add_sale_order_popup(self):
        self.ensure_one()

        partner = None
        if self.sender_email:
            partner = self.get_or_create_partner(self.sender_email)

        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_partner_id": partner.id if partner else False,
                "default_origin": f"Monitoring-{self.id}",
            }
        }





    # -------------------------------
    # Helper: extract customer message
    # -------------------------------
    def _extract_customer_message(self, raw_json_str):
        """從 Gmail JSON 或 dict抽返 snippet/plain text"""

        #print("debug::_extract_customer_message...0...")

        parsed = None
        if isinstance(raw_json_str, dict):
            parsed = raw_json_str
        elif isinstance(raw_json_str, str):
            try:
                parsed = json.loads(raw_json_str)
            except Exception:
                parsed = ast.literal_eval(raw_json_str)

        if not parsed:
            return "(no message found)"

        # 優先用 text/plain
        if "payload" in parsed:
            parts = parsed.get("payload", {}).get("parts", [])
            text_parts = [p for p in parts if p.get("mimeType") == "text/plain"]
            if text_parts:
                data = text_parts[0].get("body", {}).get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

        # fallback: snippet 或 text
        return parsed.get("snippet") or parsed.get("text") or "(no message found)"


    # -------------------------------
    # Override create: auto fill message
    # -------------------------------
    @api.model
    def create(self, vals_list):
        # Odoo 19 傳入可能係 dict 或 list
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        for vals in vals_list:
            if vals.get("original_email_body") and not vals.get("original_email_message"):
                vals["original_email_message"] = self._extract_customer_message(vals["original_email_body"])

        return super().create(vals_list)

    # -------------------------------
    # Override write: keep message updated
    # -------------------------------
    def write(self, vals):
        if vals.get("original_email_body") and not vals.get("original_email_message"):
            vals["original_email_message"] = self._extract_customer_message(vals["original_email_body"])
        return super().write(vals)
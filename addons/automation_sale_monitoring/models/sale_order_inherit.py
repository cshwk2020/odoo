import logging
from odoo import models, fields, api
_logger = logging.getLogger(__name__)

class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    monitoring_ids = fields.One2many(
        "sale.monitoring", "sale_order_id", string="Monitoring Records"
    )

    def action_quotation_send(self):
        self.ensure_one()
        template = self.env.ref("sale_monitoring.email_template_sale_order", raise_if_not_found=False)

        monitoring = self.monitoring_ids[:1]
        original_text = monitoring.original_email_body if monitoring else ""

        lines_html = "".join([
            f"<tr><td>{l.product_id.display_name}</td>"
            f"<td>{l.product_uom_qty}</td>"
            f"<td>{l.price_unit}</td></tr>"
            for l in self.order_line
        ])

        body_html = f"""
        <p><b>Original Request:</b><br>{original_text}</p>
        <p><b>Sale Order Lines:</b></p>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr><th>Product</th><th>Qty</th><th>Price</th></tr>
            {lines_html}
        </table>
        <p>
            <a href="http://127.0.0.1:5000/confirm_reply/{self.id}" 
               style="background:#28a745;color:white;padding:10px;text-decoration:none;">
                CONFIRM REPLY
            </a>
            &nbsp;&nbsp;
            <a href="http://localhost:8069/odoo/sales/{self.id}" 
               style="background:#dc3545;color:white;padding:10px;text-decoration:none;">
                GO TO FIX
            </a>
        </p>
        """

        ctx = {
            "default_model": "sale.order",
            "default_res_ids": [self.id],
            "default_use_template": bool(template),
            "default_template_id": template.id if template else False,
            "default_composition_mode": "comment",
            "default_subject": f"Quotation - {self.name}",
            "default_email_to": self.partner_id.email or "",
            "default_email_from": self.user_id.email_formatted or "",
            "default_body": body_html,
        }

        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "target": "new",
            "context": ctx,
        }


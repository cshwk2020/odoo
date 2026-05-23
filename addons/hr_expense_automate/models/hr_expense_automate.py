from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class HrExpenseAutomate(models.Model):
    _inherit = "hr.expense"

    automation_monitor = fields.Boolean(
        string="Automation Monitor",
        default=False,
        help="True if created by automation pipeline"
    )


    @api.model
    def create_with_monitor(self, expense_vals, monitor_vals):

        record = super(HrExpenseAutomate, self).create(expense_vals)
        #
        raw_image = monitor_vals.get("raw_image")
        if raw_image:
            self.env["ir.attachment"].create({
                "name": "Receipt",
                "res_model": "hr.expense",
                "res_id": record.id,
                "type": "binary",
                "datas": raw_image,
                "mimetype": "image/jpeg",
            })

        monitor_vals.update({
            "ref_id": record.id,
            "ref_url": f"/odoo/expenses/{record.id}",
        })

        monitor = self.env["automation.monitoring"].create(monitor_vals)

        return (record.id, monitor.id)
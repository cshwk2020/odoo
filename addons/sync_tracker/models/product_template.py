# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    trans_group_id = fields.Char(string="Transaction Group ID", copy=False)
    acct_sync_datetime = fields.Datetime(string="Accounting Sync Datetime")
    acct_sync_id = fields.Char(string="Accounting Sync ID")  # ProductID
    sync_status = fields.Selection([
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ], string="Sync Status", default="PENDING")

    def write(self, vals):
        exception_cols = {"acct_sync_id", "acct_sync_datetime", "sync_status"}
        if any(field not in exception_cols for field in vals.keys()):
            vals["sync_status"] = "PENDING"
        return super(ProductTemplate, self).write(vals)

# -*- coding: utf-8 -*-
from odoo import models, fields, api

import uuid


class SaleOrder(models.Model):
    _inherit = "sale.order"

    trans_group_id = fields.Char(string="Transaction Group ID", copy=False)
    acct_sync_datetime = fields.Datetime(string="Accounting Sync Datetime")
    acct_sync_id = fields.Char(string="Accounting Sync ID")  # InvoiceID
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
        return super(SaleOrder, self).write(vals)

    @api.model
    def create(self, vals):
        record = super(SaleOrder, self).create(vals)
        #record.trans_group_id = self.generate_trans_group_id(saleorder_id=record.id)
        return record

    def get_outstanding_records(self):
        return self.search([('post_sync', '=', False)])

    def prepare_xero_json(self):
        """Prepare JSON payload for Xero Invoice API"""
        invoice = {
            "Type": "ACCREC",
            "Contact": {"Name": self.partner_id.name},
            "Date": str(self.date_order),
            "DueDate": str(self.date_order),
            "InvoiceNumber": f"SO{self.id}",
            "LineItems": [{
                "Description": line.name,
                "Quantity": line.product_uom_qty,
                "UnitAmount": line.price_unit,
                "AccountCode": line.product_id.property_account_income_id.code
            } for line in self.order_line],
            "Reference": self.trans_group_id
        }
        if self.acct_sync_id:
            invoice["InvoiceID"] = self.acct_sync_id  # ✅ reuse InvoiceID if exists
        return {"Invoices": [invoice]}


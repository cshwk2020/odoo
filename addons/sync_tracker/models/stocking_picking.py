# -*- coding: utf-8 -*-
from odoo import models, fields, api
from .data_util import generate_trans_group_id

class StockPicking(models.Model):
    _inherit = "stock.picking"

    trans_group_id = fields.Char(string="Transaction Group ID", copy=False)
    acct_sync_datetime = fields.Datetime(string="Accounting Sync Datetime")
    acct_sync_id = fields.Char(string="Accounting Sync ID")  # ✅ store ManualJournalID
    pre_sync = fields.Boolean(string="Pre-Sync", default=True)
    sync = fields.Boolean(string="Sync (Hot)", default=False)
    post_sync = fields.Boolean(string="Post-Sync", default=False)

    @api.model
    def create(self, vals):
        record = super(StockPicking, self).create(vals)
        record.trans_group_id = generate_trans_group_id(picking_id=record.id)
        return record

    def get_outstanding_records(self):
        return self.search([('post_sync', '=', False)])

    def prepare_xero_json(self):
        """Prepare JSON payload for Xero Journal API (COGS)"""
        journal = {
            "Narration": f"COGS for Picking {self.name}",
            "Date": str(self.scheduled_date),
            "Reference": self.trans_group_id,
            "JournalLines": [{
                "Description": move.product_id.name,
                "Quantity": move.product_uom_qty,
                "UnitAmount": move.product_id.standard_price,
                "AccountCode": move.product_id.property_account_expense_id.code
            } for move in self.move_ids_without_package]
        }
        if self.acct_sync_id:
            journal["ManualJournalID"] = self.acct_sync_id  # ✅ reuse ManualJournalID if exists
        return {"ManualJournals": [journal]}



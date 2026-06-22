from odoo import models, fields, api
from datetime import datetime

"""
url = self.env['sync.state'].get_sync_url(
    system_name='woocommerce',
    resource_type='order'
)
# e.g. http://localhost:8888/?rest_route=/wc/v3/orders&updated_at_min=2026-06-01T00:00:00Z
"""

class SyncState(models.Model):
    _name = 'sync.state'
    _description = 'External Sync State'
    _rec_name = 'system_name'

    system_name = fields.Char(required=True)   # e.g. 'woocommerce'
    resource_type = fields.Selection([
        ('order', 'Order'),
        ('product', 'Product'),
        ('customer', 'Customer'),
        ('inventory', 'Inventory'),
    ], required=True)

    base_url = fields.Char(string="Base URL", required=True)
    last_sync_time = fields.Datetime(string="Last Sync Time")
    last_sync_id = fields.Char(string="Last Synced ID")
    active = fields.Boolean(default=True)
    notes = fields.Text(string="Notes")

    # -------------------------------
    # Helper methods
    # -------------------------------

    @api.model
    def get_sync_url(self, system_name, resource_type):
        """Return full sync URL with correct parameters based on last state"""
        tracker = self.search([
            ('system_name', '=', system_name),
            ('resource_type', '=', resource_type),
            ('active', '=', True)
        ], limit=1)

        if not tracker:
            return None

        # 基於 last_sync_time 自動生成 updated_at_min
        params = {}
        if tracker.last_sync_time:
            params['updated_at_min'] = tracker.last_sync_time.isoformat()

        if tracker.last_sync_id:
            params['since_id'] = tracker.last_sync_id

        # 拼接 URL
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{tracker.base_url}&{query}" if query else tracker.base_url

    @api.model
    def update_state(self, system_name, resource_type, sync_time=None, sync_id=None):
        """Update last sync state after successful sync"""
        tracker = self.search([
            ('system_name', '=', system_name),
            ('resource_type', '=', resource_type)
        ], limit=1)
        if tracker:
            tracker.write({
                'last_sync_time': sync_time or datetime.utcnow(),
                'last_sync_id': sync_id or tracker.last_sync_id
            })
        return tracker

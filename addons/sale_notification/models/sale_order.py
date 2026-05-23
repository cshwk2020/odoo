from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'  # Inherit the sale.order model
    def action_confirm(self):


        # Simulate live data
        live_data = {'id': 1, 'name': 'Live Data from Backend'}
        # Send the live data to the frontend using the bus service
        channel = "notification"
        message = {
            "data": live_data,
            "channel": channel
        }
        result = self.env["bus.bus"]._sendone(channel, "notification", message)


        _logger.critical(f"DEBUG0::Bus message sent: {live_data}")
        _logger.critical(f"DEBUG0::Return value: {result}")




        notification_data = {
            'type': 'success',
            'title': 'Sale Created',
            'message': f'Sale {self.name} has been created successfully!',
            'sticky': False,
        }

        # Send to multiple channels to ensure delivery
        # 1. Send to specific user
        result = self.env['bus.bus']._sendone(
            self.env.user.partner_id.id,
            'simple_notification',
            notification_data
        )

        _logger.critical(f"DEBUG2::Bus message sent: {notification_data}")
        _logger.critical(f"DEBUG2::Return value: {result}")

        # 2. Send to global channel
        result = self.env['bus.bus']._sendone(
            'notification',
            'notification',
            notification_data
        )

        # Log to confirm message was queued
        _logger.critical(f"DEBUG3::Bus message sent: {notification_data}")
        _logger.critical(f"DEBUG3::Return value: {result}")

        # 3. Send via bus channel


        _logger.critical(f"Bus notifications sent for {self.name}")






        # Call the original confirm method
        res = super(SaleOrder, self).action_confirm()
        # Add a display notification

        # In your sale creation method
        notification = {
            'type': 'simple_notification',
            'title': 'Sale Created',
            'message': f'Sale {self.name} has been created',
            'sticky': False,
        }
        self.env['bus.bus']._sendone(
            self.env.user.partner_id.id,
            'notification',
            notification
        )
        # Send to global channel
        result = self.env['bus.bus']._sendone(
            'notification',
            'notification',
            notification_data
        )

        # Log to confirm message was queued
        _logger.critical(f"DEBUG4::Bus message sent: {notification_data}")
        _logger.critical(f"DEBUG4::Return value: {result}")



        # Simulate live data
        live_data = {'id': 1, 'name': 'Live Data from Backend'}
        # Send the live data to the frontend using the bus service
        channel = "notification"
        message = {
            "data": live_data,
            "channel": channel
        }
        self.env["bus.bus"]._sendone(channel, "notification", message)

        self.env["bus.bus"]._sendone(
            "notification",
            "notification",
            {
                "type": "success",
                "title": "Sale Created",
                "message": "Your sale has been created successfully!",
                "sticky": True
            }
        )



        return True

        """ 
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Order Confirmed!',
                'message': f'Sale Order {self.name} has been successfully confirmed.',
                'type': 'success',  # Blue success notification,
                'sticky': True,   # Auto-dismiss after a few seconds
            }
        }
        """

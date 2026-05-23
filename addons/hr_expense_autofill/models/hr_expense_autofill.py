import requests
import base64
import time
import logging

from odoo import models, fields, api
from .config import IMAGE2JSON_URL

_logger = logging.getLogger(__name__)

class HrExpense(models.Model):
    _inherit = "hr.expense"

    automation_monitor = fields.Boolean(
        string="Automation Monitor",
        default=False,
        help="True if created by automation pipeline"
    )

    # --- Autofill state fields ---
    autofill_in_progress = fields.Boolean("Attach Receipt to autofill", default=False)
    progress_log = fields.Text("Autofill Progress", default="Idle")
    autofill_job_state = fields.Selection(
        [
            ("idle", "Idle"),
            ("pending", "Pending"),
            ("started", "Started"),
            ("done", "Done"),
            ("failed", "Failed"),
            ("cancelled", "Cancelled"),
        ],
        string="Autofill Job State",
        default="idle"
    )

    def _send_bus_notification(self, data):
        """Send bus notification with fresh transaction"""
        # Get a fresh cursor
        db_name = self.env.cr.dbname
        registry = self.env.registry

        with registry.cursor() as cursor:
            fresh_env = api.Environment(cursor, self.env.uid, self.env.context)
            fresh_env['bus.bus']._sendone('notification', 'notification', {"data": data})
            cursor.commit()
            _logger.critical(f"Bus notification: {data}")



    # --- Defaults ---
    @api.model
    def default_get(self, fields_list):
        """Set default values for required fields"""
        defaults = super().default_get(fields_list)

        # Default name
        if 'name' in fields_list and not defaults.get('name'):
            defaults['name'] = 'Pending Autofill'

        # Default total amount
        if 'total_amount' in fields_list and not defaults.get('total_amount'):
            defaults['total_amount'] = 0.0

        # Clear taxes
        self.tax_ids = [(5, 0, 0)]

        # Default product (category)
        if 'product_id' in fields_list and not defaults.get('product_id'):
            #product = self.env['product.product'].search([('default_code', '=', 'EXP_GEN')], limit=1)
            #if product:
            #    defaults['product_id'] = product.id
            product = self.env['product.product'].search([('can_be_expensed', '=', True)], limit=1)
            if product:
                defaults['product_id'] = product.id

    # Default employee
        if 'employee_id' in fields_list and not defaults.get('employee_id'):
            employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            if employee:
                defaults['employee_id'] = employee.id

        return defaults


    # --- Dropdown helper ---
    def _fetch_expense_dropdowns(self):
        categories = self.env['product.product'].search_read(
            [('can_be_expensed', '=', True)], ['id', 'name', 'code']
        )
        employee = self.env['hr.employee'].search_read([('user_id', '=', self.env.uid)], ['id', 'name', 'parent_id'])
        employee_data = employee[0] if employee else {}
        manager_data = {}
        if employee_data and employee_data.get('parent_id'):
            manager = self.env['hr.employee'].browse(employee_data['parent_id'][0])
            manager_data = {'id': manager.id, 'name': manager.name}
        payment_modes = [
            {'value': 'own_account', 'label': 'Employee (to reimburse)'},
            {'value': 'company_account', 'label': 'Company'}
        ]
        return {
            'categories': categories,
            'employee': employee_data,
            'manager': manager_data,
            'payment_modes': payment_modes
        }


    # --- Attach receipt (synchronous) ---
    def attach_document(self, **kwargs):
        res = super().attach_document(**kwargs)
        attachment_ids = kwargs.get('attachment_ids', [])
        if attachment_ids:
            attachment = self.env['ir.attachment'].browse(attachment_ids[-1])
            if attachment.mimetype and attachment.mimetype.startswith("image"):
                self._message_set_main_attachment_id(attachment, force=True)
                # Update progress BEFORE API call
                self.write({
                    "progress_log": "Autofill running… please wait (up to 2 minutes)",
                    "autofill_in_progress": True,
                    "autofill_job_state": "started",
                })
            # Get the base64 data from attachment
            image_b64 = attachment.datas

            # If it's bytes, decode to string
            if isinstance(image_b64, bytes):
                image_b64 = image_b64.decode('utf-8')

            # Remove any existing prefix
            if ',' in image_b64:
                image_b64 = image_b64.split(',')[1]

            # Add the proper Data URL prefix
            mimetype = attachment.mimetype or 'image/jpeg'
            image_data_url = f"data:{mimetype};base64,{image_b64}"

            _logger.info(f"Image data URL length: {len(image_data_url)}")
            _logger.info(f"Prefix: {image_data_url[:50]}")


            live_data = {'id': 1, 'name': 'Autofill Pending...might up to 2 minutes...'}
            self._send_bus_notification(live_data)
            _logger.critical(f"MYDEBUG0::Notification sent: {live_data}")



            # Don’t bother stripping prefix — Odoo doesn’t add one
            # self.process_autofill_with_image(image_data_url)
            self.process_autofill_with_image(image_data_url)
            _logger.critical(f"MYDEBUG20::Notification sent: {live_data}")

            #
            live_data = {'id': 100, 'name': 'Autofill Done...'}
            self._send_bus_notification(live_data)
            _logger.critical(f"MYDEBUG30::Notification sent: {live_data}")


        return {'type': 'ir.actions.client', 'tag': 'reload'}




    # --- Autofill process (inline) ---
    def process_autofill_with_image(self, image_b64):

        self.ensure_one()

        try:
            self.write({
                "progress_log": "Processing receipt...",
                "autofill_job_state": "pending",
                "autofill_in_progress": True,
            })

            expense_dropdowns = self._fetch_expense_dropdowns()

            resp = requests.post(
                IMAGE2JSON_URL,
                json={
                    "expense_dropdowns": expense_dropdowns,
                    "module": "expense",
                    "receipt_image": image_b64,
                    "expense_id": self.id
                },
                timeout=3
            )


            _logger.critical(f"MYDEBUG...C...::process_autofill_with_image")



        except requests.exceptions.Timeout:

            _logger.critical(f"MYDEBUG...D...::process_autofill_with_image")

            #
            live_data = {'id': -10, 'name': f'Autofill API Timeout...'}
            self._send_bus_notification(live_data)
            _logger.critical(f"MYDEBUG...D...::Notification sent: {str(live_data)}")


            self.write({
                "progress_log": "Autofill timed out.",
                "autofill_job_state": "failed",
                "autofill_in_progress": False,
            })


        except Exception as e:

            _logger.critical(f"MYDEBUG...E...::process_autofill_with_image")


            self.write({
                "progress_log": f"Error: {str(e)}",
                "autofill_job_state": "failed",
                "autofill_in_progress": False,
            })

        _logger.critical(f"MYDEBUG...E-RESP...::process_autofill_with_image", resp)


        if resp.status_code != 200:
            _logger.critical(f"MYDEBUG...F...::process_autofill_with_image")

            self.write({
                "progress_log": f"API error: {resp.text}",
                "autofill_job_state": "failed",
                "autofill_in_progress": False,
            })

            #
            live_data = {'id': -20, 'name': f'Autofill Error...{resp.text}...'}
            self._send_bus_notification(live_data)
            _logger.critical(f"MYDEBUG10::Notification sent: {live_data}")

        else:

            data = resp.json().get('data', {})
            _logger.critical(f"MYDEBUG...G...::process_autofill_with_image")

            notes = data.get("summary", {}).get("notes", "")

            _logger.critical(f"MYDEBUG...H...::process_autofill_with_image")

            if data.get("details"):
                notes += "\n\nItems:\n"
                for item in data.get("details", []):
                    notes += f"- {item.get('quantity', 1)} x {item.get('item', 'Item')}: ${item.get('price_unit', 0)}\n"

            _logger.critical(f"MYDEBUG...I...::process_autofill_with_image")

            update_vals = {
                "name": data.get("summary", {}).get("name", "Expense"),
                "total_amount": data.get("summary", {}).get("total_amount", 0.0),
                "date": data.get("summary", {}).get("date"),
                "payment_mode": data.get("summary", {}).get("paid_by", "own_account"),
                "description": notes,
                "progress_log": "Autofill complete!",
                "autofill_job_state": "done",
                "autofill_in_progress": False
            }
            _logger.critical(f"MYDEBUG...J...::process_autofill_with_image")

            update_vals = {k: v for k, v in update_vals.items() if v is not None}
            self.write(update_vals)

            _logger.critical(f"MYDEBUG...K...::process_autofill_with_image")





    # --- Cancel action ---
    def action_cancel_autofill(self):
        self.ensure_one()
        self.write({
            "progress_log": "Cancelled.",
            "autofill_job_state": "cancelled",
            "autofill_in_progress": False,
        })

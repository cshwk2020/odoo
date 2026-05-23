# hr_expense_autofill/controllers/autofill_controller.py
from odoo import http
from odoo.http import request

class AutofillController(http.Controller):
    @http.route('/expense/autofill_feedback/<int:expense_id>', type='json', auth='user')
    def get_feedback(self, expense_id):
        expense = request.env['hr.expense'].browse(expense_id)
        return {'message': expense.progress_log or "No feedback yet"}


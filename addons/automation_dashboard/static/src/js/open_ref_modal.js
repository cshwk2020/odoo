/** @odoo-module **/

import { registry } from "@web/core/registry";
import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog";

const actionRegistry = registry.category("actions");

actionRegistry.add("open_expense_in_modal", async (env, action) => {
    const { dialog } = env.services;
    const expenseId = action.params.expense_id;

    dialog.add(FormViewDialog, {
        resModel: "hr.expense",
        resId: expenseId,
        title: "Expense Details",
        onRecordSaved: async () => {
            await env.reload(); // refresh monitoring list
        },
    });
});

actionRegistry.add("open_invoice_in_modal", async (env, action) => {
    const { dialog } = env.services;
    const invoiceId = action.params.invoice_id;

    dialog.add(FormViewDialog, {
        resModel: "account.move",
        resId: invoiceId,
        title: "Invoice Details",
        onRecordSaved: async () => {
            await env.reload(); // refresh monitoring list
        },
    });
});


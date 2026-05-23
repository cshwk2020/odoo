
odoo.define('hr_expense_autofill.attach_receipt_context', function(require) {
    "use strict";

    var FormController = require('web.FormController');

    FormController.include({
        _onButtonClick: function(event) {
            var $target = $(event.currentTarget);
            var buttonName = $target.data('name') || $target.attr('name');

            // Check if this is the attach receipt button
            if ($target.closest('.o_widget_attach_document').length ||
                buttonName === 'action_attach_receipt') {

                // Add context to the action
                var context = this.model.get(this.handle, { raw: true }).getContext() || {};
                context.skip_validation = true;
                this.model.setContext(context);
            }

            return this._super(event);
        }
    });
});


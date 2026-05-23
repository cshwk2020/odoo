// hr_expense_autofill/static/src/js/autofill_feedback.js
import { Component, useState, onWillStart } from "@odoo/owl";

export class AutofillFeedbackComponent extends Component {
    static template = "hr_expense_autofill.AutofillFeedback";

    setup() {
        this.state = useState({ msg: "Waiting for autofill..." });

        const bus = this.env.services.bus_service;
        bus.addChannel("autofill_feedback");
        bus.onNotification(this, (notif) => {
            if (notif.type === "autofill_feedback") {
                this.state.msg = notif.payload.message;
            }
        });
    }
}

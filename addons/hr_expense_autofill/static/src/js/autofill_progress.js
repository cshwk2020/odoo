odoo.define('hr_expense_autofill.progress', function (require) {
    "use strict";

    const BusService = require('bus.BusService');
    const { registry } = require('@web/core/registry');

    // Extend the bus service
    const myProgressService = {
        start(env) {
            const bus = env.services.bus_service;
            bus.addChannel('autofill_progress');   // subscribe to your channel
            bus.onNotification(this, (notif) => {
                if (notif.type === 'autofill_progress') {
                    const data = notif.payload;
                    const box = document.getElementById('progress_box');
                    if (box) {
                        box.innerText = data.message || data.progress_log;
                    }
                }
            });
        },
    };

    registry.category('services').add('hr_expense_autofill.progress', myProgressService);
});

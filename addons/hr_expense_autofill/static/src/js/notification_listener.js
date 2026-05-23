/** @odoo-module **/
import { registry } from "@web/core/registry";

console.log("=== NOTIFICATION LISTENER FILE LOADED ===");

const busNotificationService = {
    dependencies: ["bus_service", "notification"],

    start(env) {
        console.log('busNotificationService...addEventListener...debug...start(env)...');

        const bus = env.services.bus_service;
        const notification = env.services.notification;

        console.log('DEBUG...bus', bus);
        console.log('DEBUG...notification', notification);

        // Subscribe to the channel you used in _sendone
        bus.addChannel("notification");
        console.log('busNotificationService...addEventListener...debug...bus.addChannel...');
        // Listen for incoming notifications
        /*
        bus.subscribe("notification", (notif) => {
            console.log('busNotificationService...addEventListener...debug...0...', notif);
            if (notif.type === "notification") {
                console.log('busNotificationService...addEventListener...debug...10...');
                const payload = notif.payload;
                console.log('busNotificationService...addEventListener...debug...20...', payload);
                notification.add(payload.message, {
                    title: payload.title,
                    type: payload.type || "info",
                    sticky: payload.sticky || false,
                });
                console.log('busNotificationService...addEventListener...debug...30...add...');
            }
        });
        */

        bus.subscribe("notification", (notif) => {
            console.log('DEBUG...0...Notification received...0....', notif);

            // The actual structure is {data: {...}, channel: 'notification'}
            // Extract the data from the 'data' property
            const payload = notif.data || notif;

            console.log('DEBUG...10...Extracted payload:', payload);

            // Check if we have a message to display
            if (payload && payload.message) {
                console.log('DEBUG...20...Extracted payload:', payload);
                notification.add(payload.message, {
                    title: payload.title || "Notification",
                    type: payload.type || "info",
                    sticky: payload.sticky || true,
                });
                console.log('DEBUG...30...after notification.add...');
            }
            // Also handle the live_data format
            else if (payload && payload.name && payload.id) {
                console.log('DEBUG...120...Extracted payload:', payload);
                notification.add(`Live Data: ${payload.name} (ID: ${payload.id})`, {
                    title: "Live Data Update",
                    type: "info",
                    sticky: true,
                });
            }
            else {
                console.log('DEBUG...220...No message field found in payload:', payload);
            }
        });



    },
};

registry.category("services").add("bus_notification_listener", busNotificationService);
console.log('busNotificationService...addEventListener...debug...40...registry.category add...', busNotificationService);
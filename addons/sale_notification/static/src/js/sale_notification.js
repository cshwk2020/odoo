/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
export class SaleNotificationButton extends owl.Component {
   static template = "sale_notification.SaleNotificationButton";
   static props = [
       "record", // The record data
       "readonly", // Whether the field is readonly
       "*" // Wildcard to allow additional props
   ];
   setup() {
       this.notification = useService("notification");
   }
   onClick() {
       this.notification.add("Order Info!", {
           title: "Sale Order Alert",
           type: "info",
           'sticky': true,
       });
   }
}
registry.category("fields").add("sale_notification_button", {
   component: SaleNotificationButton,
});

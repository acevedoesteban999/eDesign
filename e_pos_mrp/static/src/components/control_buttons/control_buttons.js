/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { _t } from "@web/core/l10n/translation";

patch(ControlButtons.prototype, {
    
    clickPicking() {
        // const order = this.pos.get_order();
        // const partner = order.get_partner();
        // const searchDetails = partner ? { fieldName: "PARTNER", searchTerm: partner.name } : {};
        this.pos.showScreen("PickingScreen");
    }
});


/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { _t } from "@web/core/l10n/translation";

patch(ControlButtons.prototype, {
    
    async createManofacture() {
        await this.pos.action.doAction({
            'name': _t('Create Manufacture'),
            'type': 'ir.actions.act_window',
            'res_model': 'e_pos_mrp.creata_order_wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'views': [[false,'form']],
            'domain': [],
            'context': {},
        });
    }
});


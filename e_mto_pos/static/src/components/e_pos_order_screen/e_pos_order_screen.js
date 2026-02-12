import { _t } from "@web/core/l10n/translation";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { ePosOrderScreen } from "@e_pos_base/components/e_pos_order_screen/e_pos_order_screen"
import { patch } from "@web/core/utils/patch";

patch( ePosOrderScreen.prototype,{
    onConfirmPicking(){
        this.dialog.add(ConfirmationDialog, {
            title: _t("Confirm Delivery ?"),
            body: _t("Are you sure that the customer wants to recive the picking?"),
            confirm: async () => this.ConfirmPicking(this.state.selectedPosOrder),
            cancel: ()=>{}
        });
    },

    async ConfirmPicking(pos_order){

        await this.pos.data.call(
            "stock.picking",
            "confirm_picking",
            [],
            {picking_id: pos_order.picking_pos_mrp[0]}
        ); 
        this.notification.add(
            _t("Success confirmation for Delivery %s in POS order: %s")
                .replace("%s", pos_order.picking_pos_mrp[1])
                .replace("%s", pos_order.pos_reference),
            {
                type: "success",
                title: _t("Success"),
                autocloseDelay: 3000,
            }
        );
        this.closePosOrderScreen();
    },

    _getPickingStates() {
        return {
            'waiting':     { text: _t("Waiting"),     decoration: 'badge-warning' },
            'confirmed': { text: _t("Confirmed"), decoration: 'badge-info' },
            'assigned':     { text: _t("Ready"),     decoration: 'badge-success' },
            'done':     { text: _t("Done"),     decoration: 'badge-secondary' },
            'cancel':   { text: _t("Cancel"),   decoration: 'badge-danger' },
        };
    },
    
    getPickingStateData(stateKey) {
        return this._getPickingStates()[stateKey] ?? { 
            text: stateKey, 
            decoration: 'badge-secondary' 
        };
    },
    
    getPickingStateText(stateKey) {
        return this.getPickingStateData(stateKey).text;
    },
    
    getPickingStateDecoration(stateKey) {
        return this.getPickingStateData(stateKey).decoration;
    },
})



    

    
   

    
   
    


    


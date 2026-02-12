import { _t } from "@web/core/l10n/translation";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { ePosOrderScreen } from "@e_pos_base/components/e_pos_order_screen/e_pos_order_screen"
import { patch } from "@web/core/utils/patch";

patch( ePosOrderScreen.prototype,{
    onConfirmPicking(){
        this.dialog.add(ConfirmationDialog, {
            title: _t("Confirm Delivery ?"),
            body: _t("Are you sure that the customer wants to recive the picking?"),
            confirm: () => this.ConfirmPicking(this.state.selectedPosOrder),
        });
    },

    async ConfirmPicking(pickingLine){
        await this._confirmPicking(pickingLine)
    },

    async _confirmPicking(pickingLine) {
        await this.pos.data.call(
            "stock.picking",
            "confirm_picking",
            [],
            {picking_id: pickingLine.id}
        ); 
        this.notification.add(
            _t("Success confirmation for Delivery %s in POS order: %s")
                .replace("%s", pickingLine.name)
                .replace("%s", pickingLine.pos_order_pos_reference),
            {
                type: "success",
                title: _t("Success"),
                autocloseDelay: 3000,
            }
        );
        this.closePosOrderScreen();
    },
})



    

    
   

    
   
    


    


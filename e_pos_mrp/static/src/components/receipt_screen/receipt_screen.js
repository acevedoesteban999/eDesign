import { patch } from "@web/core/utils/patch";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { _t } from "@web/core/l10n/translation";
import { onMounted } from "@odoo/owl";

patch(ReceiptScreen.prototype,{
    async _get_hasPicking(order_id){
          let response =  await this.pos.data.call(
            "stock.picking",
            "read_picking_by_pos_order",
            [],
            {pos_order_id: order_id}
        ); 
        if (response)
            return response
        else
            return {'picking_id':false,'mrp_production_count':0}
    },
    setup(){
        super.setup()
        this.state.picking_id = false
        this.state.pos_order_id = false
        onMounted(async () => {
            const order = this.pos.get_order();
            let { picking_id , mrp_production_count } = await this._get_hasPicking(order?.id||null)
            this.state.picking_id = picking_id
            this.state.mrp_production_count = mrp_production_count
            this.state.pos_order_id = order
        });


    }
})
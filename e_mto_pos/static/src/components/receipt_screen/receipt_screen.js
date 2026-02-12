import { patch } from "@web/core/utils/patch";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { _t } from "@web/core/l10n/translation";
import { onMounted } from "@odoo/owl";

patch(ReceiptScreen.prototype,{
    
    setup(){
        super.setup()
        this.state.picking_id = false
        this.state.pos_order_id = false
        onMounted(async () => {
            const order = this.pos.get_order();
            if (order){
                let response = await this.pos.data.call(
                    "stock.picking",
                    "read_picking_by_pos_order",
                    [],
                    {pos_order_id: order.id}
                ); 
                if(response){
                    this.state.show_mrp_picking = true
                    this.state.pos_reference = response.pos_reference
                    this.state.tracking_number = response.tracking_number
                    this.state.picking_pos_mrp_name = response.picking_pos_mrp_name
                }
            }
        });


    }
})
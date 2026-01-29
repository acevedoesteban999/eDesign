import { patch } from "@web/core/utils/patch";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";

patch(PosOrderline.prototype,{
    can_be_merged_with(orderline){
        return super.can_be_merged_with(orderline) && (orderline.design_id?.id === this.design_id?.id )
    },
    getDisplayData() {
        let data = super.getDisplayData()
        return {
            ...data,
            design_id: this.design_id?{'default_code':this.design_id.default_code}:false
        }
    }
})

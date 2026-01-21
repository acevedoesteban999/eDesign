import { patch } from "@web/core/utils/patch";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";

patch(PosOrderline.prototype,{
    can_be_merged_with(orderline){
        return super.can_be_merged_with(orderline) && (orderline.design_id?.[0] === this.raw.design_id?.[0] )
    },
    getDisplayData() {
        let data = super.getDisplayData()
        return {
            ...data,
            design_display_name: this.raw.design_id?.[1]
        }
    }
})

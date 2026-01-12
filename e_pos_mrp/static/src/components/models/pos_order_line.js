import { patch } from "@web/core/utils/patch";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { _t } from "@web/core/l10n/translation";


patch(PosOrderline.prototype,{   
    getDisplayData() {
        let data = super.getDisplayData()
        return {
            ...data,
            has_create_pos_mrp: this.product_id.raw.has_create_pos_mrp
        }
    }
})

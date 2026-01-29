import { ProductConfiguratorPopup } from "@point_of_sale/app/store/product_configurator_popup/product_configurator_popup";
import { patch } from "@web/core/utils/patch";

patch(ProductConfiguratorPopup.prototype,{
    hideOutStock(){
        if(this.pos.config.hide_out_stock)
            return this.state.product.raw.qty_available <= 0 && !(this.state.product.raw.can_show_in_pos_out_stock || false)
    }
})
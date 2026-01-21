import { patch } from "@web/core/utils/patch";
import { ProductProduct } from "@point_of_sale/app/models/product_product";

patch(ProductProduct.prototype,{
    // isConfigurable() {
    //     return this._isConfigurable() || this.raw.has_design
    // },

    // _isConfigurable(){
    //     return super.isConfigurable()
    // },
})
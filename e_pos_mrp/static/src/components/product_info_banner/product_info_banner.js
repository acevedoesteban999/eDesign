import { ProductInfoBanner } from "@point_of_sale/app/components/product_info_banner/product_info_banner"
import { patch } from "@web/core/utils/patch";

patch(ProductInfoBanner.prototype,{
    setup(){
        super.setup()
        this.has_create_pos_mrp = this.props.product.raw.has_create_pos_mrp
    },
})
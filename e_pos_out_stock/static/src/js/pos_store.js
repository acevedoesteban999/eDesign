/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    async _compute_hide_out_stock_data(){
        const products = this.models["product.product"].getAll();
        if (products.length) {   
            const product_ids = products.map(p => p.id);

            try {
                const qty_data = await this.data.call(
                    "product.product",
                    "read",
                    [product_ids, ["qty_available","can_show_in_pos_out_stock"]]
                );
                
                qty_data.forEach((prod) => {
                    const localProd = this.models["product.product"].get(prod.id);
                    if(!(localProd.id in this.mainProductVariant))
                        localProd.raw.qty_variants_available = 0
                })

                qty_data.forEach((prod) => {
                    const localProd = this.models["product.product"].get(prod.id);
                    if (localProd){
                        if(prod.qty_available && localProd.id in this.mainProductVariant){
                            const mainVariant = this.models["product.product"].get(this.mainProductVariant[localProd.id].id)
                            if(mainVariant.raw.qty_variants_available)
                                mainVariant.raw.qty_variants_available += prod.qty_available
                            else
                                mainVariant.raw.qty_variants_available = prod.qty_available
                        }
                        localProd.raw.qty_available = prod.qty_available ?? 0;
                        localProd.raw.can_show_in_pos_out_stock = prod.can_show_in_pos_out_stock ?? false;
                    
                    } 
                });

                
            } catch (err) {}
        }
    },
    async afterProcessServerData() {
        await this._compute_hide_out_stock_data()
        return await super.afterProcessServerData?.(...arguments);
    },
});
/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    async afterProcessServerData() {
        const products = this.models["product.product"].getAll();
        if (products.length) {   
            const product_ids = products.map(p => p.id);

            try {
                const qty_data = await this.data.call(
                    "product.product",
                    "read",
                    [product_ids, ["has_create_pos_mrp"]]
                );
                
                qty_data.forEach((prod) => {
                    const localProd = this.models["product.product"].get(prod.id);
                    if (localProd){
                        localProd.raw.has_create_pos_mrp = prod.has_create_pos_mrp ?? false;
                    } 
                });

                
            } catch (err) {}
        }
        return await super.afterProcessServerData?.(...arguments);
    },
});
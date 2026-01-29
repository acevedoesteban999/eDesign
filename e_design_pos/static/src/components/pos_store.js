/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { EDesignConfiguratorPopup } from "./edesign_configurator_popup/edesign_configurator_popup"

patch(PosStore.prototype, {
    async afterProcessServerData() {
        const products = this.models["product.product"].getAll();
        if (products.length) {   
            const product_ids = products.map(p => p.id);
            try {
                const qty_data = await this.data.call(
                    "product.product",
                    "read",
                    [product_ids, ["has_design",'design_ids']]
                );
                
                qty_data.forEach((prod) => {
                    const localProd = this.models["product.product"].get(prod.id);
                    if (localProd){
                        localProd.raw.has_design = prod.has_design ?? false;
                        localProd.raw.design_ids = prod.design_ids ?? []
                    } 
                });

                
            } catch (err) {}
        }
        return await super.afterProcessServerData?.(...arguments);
    },

    async addLineToOrder(vals, order, opts = {}, configure = true) {
        
        if (typeof vals.product_id == "number") {
            vals.product_id = this.data.models["product.product"].get(vals.product_id);
        }
        if(vals.product_id.raw.has_design){
            const payload = await makeAwaitable(this.dialog, EDesignConfiguratorPopup, {
                product: vals.product_id,
            });
            if (payload === undefined)
                return
            vals.design_id = payload?.design_id ?? false
        }
        return super.addLineToOrder(vals, order, opts, configure)
    },
});
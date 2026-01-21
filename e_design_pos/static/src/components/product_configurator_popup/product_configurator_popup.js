import { patch } from "@web/core/utils/patch";
import { ProductConfiguratorPopup } from "@point_of_sale/app/store/product_configurator_popup/product_configurator_popup";
import { EDesignSelection } from "@e_design/components/edesign_selection/edesign_selection"
import { onWillStart } from '@odoo/owl';
import { useService } from "@web/core/utils/hooks";

patch(ProductConfiguratorPopup,{
    components: {
        ...ProductConfiguratorPopup.components,
        EDesignSelection,
    }

})

patch(ProductConfiguratorPopup.prototype,{
    setup(){
        super.setup()
        this.has_design = this.props.product.raw.has_design
        this.is_simple_product = this.getVariantAttributeValueIds().length === 0
        this.orm = useService('orm')
        this.design = {}
        onWillStart(async ()=>{
            this.designs = await this.orm.call(
                'product.edesign',
                'read',
                [this.props.product.raw.design_ids,['display_name','image']]
            )
        })
    },
    computePayload() {
        let payload = super.computePayload()
        if(this.has_design)
            payload.design_id = [this.design.id,this.design.display_name]
        return payload
    },

})
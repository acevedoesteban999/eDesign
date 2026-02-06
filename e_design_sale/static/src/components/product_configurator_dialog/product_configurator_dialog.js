import { _t } from "@web/core/l10n/translation";
import { ProductConfiguratorDialog } from "@sale/js/product_configurator_dialog/product_configurator_dialog";
import { patch } from "@web/core/utils/patch";
import { onWillStart, useState } from '@odoo/owl';
import { useService } from "@web/core/utils/hooks";
import { EDesignSelection } from "@e_design/components/edesign_selection/edesign_selection"

patch(ProductConfiguratorDialog, {
    props: {
        ...ProductConfiguratorDialog.props,
        record : {type: Object, optional: true}
    }
})

patch(ProductConfiguratorDialog, {
    components: {
        ...ProductConfiguratorDialog.components,
        EDesignSelection,
    },
})

patch(ProductConfiguratorDialog.prototype,{
    setup(){
        super.setup()
        this.orm = useService('orm')
        this.design = {}
    
        onWillStart(async ()=>{
            const res = await this.orm.call(
                'product.template',
                'read',
                [this.props.productTemplateId,['design_ok','design_ids']]
            )
            this.has_design = res[0]?.design_ok && res[0]?.design_ids.length > 0 
            if(this.has_design){
                const res1 =await this.orm.call(
                    'product.edesign',
                    'read',
                    [res[0]?.design_ids,['display_name','image']]
                )
                this.designs = res1
            }
        })
    },

    async onConfirm(options) {
        if(this.has_design){
            let design = false
        
            if(this.design)
                design = [this.design.id , this.design.display_name]
        
            this.props.record.update({
                design_id: design,
            })
            
        }
        this.props.record.fromOnConfirm = true
        await super.onConfirm(options)
    }
})

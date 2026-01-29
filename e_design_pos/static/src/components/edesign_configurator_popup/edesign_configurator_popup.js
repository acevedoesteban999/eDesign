import { EDesignSelection } from "@e_design/components/edesign_selection/edesign_selection"
import { onWillStart } from '@odoo/owl';
import { Dialog } from "@web/core/dialog/dialog";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class EDesignConfiguratorPopup extends Component {
    static template = "e_design_pos.EDesignConfiguratorPopup"
   
    static components = {
        Dialog,
        EDesignSelection,
    };

    static props = ["product", "getPayload", "close"];

    setup() {
        this.pos = usePos();
    
        this.design = {}
    
        onWillStart(async ()=>{
            this.designs = await this.pos.data.orm.call(
                'product.edesign',
                'read',
                [this.props.product.raw.design_ids,['display_name','image']]
            )
        })
    }

    computePayload() {
        if(this.design?.id)
            return {
                design_id : this.pos.models['product.edesign'].get(this.design.id)
            }
        return false
    }
    close() {
        this.props.close();
    }
    confirm() {
        this.props.getPayload(this.computePayload());
        this.props.close();
    }
}

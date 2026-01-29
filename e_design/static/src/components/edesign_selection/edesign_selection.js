/** @odoo-module **/
import { Component, useState } from "@odoo/owl";

export class EDesignSelection extends Component {
    static template = "e_design.EDesignSelection";
    static props = {
        design_id: {type: [Number,Boolean], optional: true},
        designs: {
            type: Array, 
            element: {
                type: Object,
                optional: true,
                shape: {
                    id: Number,
                    display_name: String,
                    image: [String,Boolean],
                },
            },
        },
        update: Function,
    };
    static defaultProps = {
        design_id: false,
    }
    setup() {
      this.state = useState({
        design: {},
      })
      if(this.props.design_id)
        this.onChangeDesign(this.props.design_id)
    }

    onChangeDesign(designId){
        if (!designId){          
            this.state.design = {};
        }else{
            const design = this.props.designs.find(v => v.id === Number(designId));
            this.state.design = design;
        }
        this.props.update(this.state.design)
    }
}

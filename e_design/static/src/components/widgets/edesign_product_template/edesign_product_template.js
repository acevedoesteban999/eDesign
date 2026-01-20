/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component , onWillStart , useState } from "@odoo/owl";
import { loadCSS , loadJS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";

export class EDesignProduct extends Component {
    static template = "e_design.eDesignProductTemplate";
    static props = {
        ...standardFieldProps,
    };
    setup() {
      this.state = useState({
        'designs':[],
        // 'design_counter': 0,
      });
      

      this.orm = useService('orm');
      this.action = useService("action");
      onWillStart(async () => {
        await this.getDesigns();
      });
    }

    async getDesigns(reload=false){
      let designIds  = this.props.record.data[this.props.name]._currentIds
      if (reload) {
        const readRes = await this.orm.call(
            'product.template',
            'read',
            [[this.props.record.resId], ['design_ids']]
        );
        designIds = readRes[0]?.design_ids || [];
    }
      this.state.designs = await this.orm.call(
        'product.edesign',
        'read',
        [designIds ,['id','name','default_code']]
      )
      // this.state.design_counter = this.state.designs.length
    }
    
    _doDesignAction(method,context){
      return this.action.doAction(
        this.orm.call(
          'product.edesign',
          'get_design_action',
          [method,context],
        ),
        {
           onClose: async (infos) => {
              await this.getDesigns(true);
              await this.props.record.model.load()
          },
        }
      )
    }

    createDesign(){
      return this._doDesignAction(        
        'create',
        {
          'default_product_id':this.props.record.data.id
        },
      )
    }

    linkDesign(){
      return this._doDesignAction(
        'link',
        {
          'default_product_id':this.props.record.data.id
        },
      )
    }
    
    openDesign(record){
      return this._doDesignAction(
        'open',
        {
          'product_design_id':record
        },
      )
    }

    unlinkDesign(record){
      // return this._doDesignAction(
      //   'unlink',
      //   {
      //     'default_design_id':record,
      //     'default_product_id':this.props.record.data.id,
      //   }
      // )
    }
    
}








const eDesignProduct = {
  displayName: 'eDesign Product Template',
  component: EDesignProduct,
  supportedTypes: ['many2many'],
  extractProps: ({ attrs }) => ({
    name: attrs.name,
  }),
};

registry.category("fields").add("edesign_product_template", eDesignProduct);

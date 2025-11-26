/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component , onWillStart , useState } from "@odoo/owl";
import { loadCSS , loadJS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";

export class ProductDesign extends Component {
    static template = "e_design.ProductDesign";
    static props = {
        ...standardFieldProps,
    };
    setup() {
      this.state = useState({
        'designs_attr_values':[],
        'ref':{},
      });
      

      this.orm = useService('orm');
      this.action = useService("action");
      onWillStart(async () => {
        await this.getData();
      });
    }

    async getData(){
      this.state.designs_attr_values = await this.orm.call(
        'product.design',
        'get_data_for_product_template_view',
        this.props.record.data.attribute_line_ids.currentIds,
        {},
      )
    }
    

    addDesign(){
      return this.action.doAction(
        this.orm.call(
          'product.design','get_design_action',[],{'product_id':this.props.record.data.id}
        ),
        {
          onClose: (infos) => {
            this.getData();
            this.props.record.model.load();
            this.render(true);
          },
        }
      )
    }
    
    openDesign(record){
      return this.action.doAction(
        this.orm.call(
          'product.design','get_design_action',[],{'product_design_id':record}
        ),
        {
          onClose: (infos) => {
            this.getData();
            this.props.record.model.load();
            this.render(true);
          },
        }
      )
    }
}








const productDesign = {
  displayName: 'Design Attr Values',
  component: ProductDesign,
  supportedTypes: ['one2many'],
  extractProps: ({ attrs }) => ({
    name: attrs.name,
  }),
};

registry.category("fields").add("product_design", productDesign);

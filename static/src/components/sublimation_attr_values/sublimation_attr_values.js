/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component , useState , toRaw } from "@odoo/owl";
import { loadCSS , loadJS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";

export class Sublimation_attr_values extends Component {
    static template = "e_sublimation.Sublimation_attr_values";
    static props = {
        ...standardFieldProps,
    };
    setup() {
      this.state = useState({
        'attr_values':[]
      });
      this.orm = useService('orm');
      // console.log(this.props.record.data.attribute_line_ids)
      // console.log(toRaw(this.props.record.data.attribute_line_ids.currentIds))
      this.getData();
    }

    async getData(){
      this.state.attr_values = await this.orm.call(
        'product.design',
        'get_data_for_product_template_view',
        this.props.record.data.attribute_line_ids.currentIds,
        {},
      )
    }
}

const sublimationAttrValues = {
  displayName: 'Sublimation Attr Values',
  component: Sublimation_attr_values,
  supportedTypes: ['one2many'],
  extractProps: ({ attrs }) => ({
    name: attrs.name,
  }),
};

registry.category("fields").add("sublimation_attr_values", sublimationAttrValues);

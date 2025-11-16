/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

export class Sublimation_attr_values extends Component {
    static template = "e_sublimation.Sublimation_attr_values";
    static props = {
        ...standardFieldProps,
    };
    setup() {
      console.log(this)
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

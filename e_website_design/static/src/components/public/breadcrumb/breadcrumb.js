/** @odoo-module **/
import { Component } from "@odoo/owl";
  
  export class BreadcrumbComponent extends Component {
      static template = "e_website_design.BreadcrumbComponent";
      static props = [
        'back_url','breadcrumbs',
      ]
      setup() {}
  }
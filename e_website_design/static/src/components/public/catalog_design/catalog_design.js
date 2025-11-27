/** @odoo-module **/

import { Component , onWillStart , useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { loadCSS , loadJS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";
import { BreadcrumbComponent } from "../breadcrumb/breadcrumb"

  export class CatalogDesignComponent extends Component {
      static template = "e_website_design.CatalogDesignComponent";
      static components = {BreadcrumbComponent};
      static props = ['back_url?','breadcrumbs?']

      setup() {
          this.state = useState({
            'designs': [],
            'domain':[],
          })
          this.back_url = this.props.back_url || ''
          this.breadcrumbs = this.props.breadcrumbs || []

          this.orm = useService('orm')
          
          onWillStart(async ()=>{
              await this.getData()
          })
      }

      async getData(){
        this.state.designs = await this.orm.searchRead(
          'product.design',
          this.state.domain,
          ['id','name','default_code']
        )
      }

  }

  registry.category("public_components").add("e_website_design.CatalogDesignComponent", CatalogDesignComponent);
  
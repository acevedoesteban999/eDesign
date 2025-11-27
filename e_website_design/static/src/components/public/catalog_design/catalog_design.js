/** @odoo-module **/

import { Component , onWillStart , useState , useRef , onRendered} from "@odoo/owl";
import { registry } from "@web/core/registry";
import { loadCSS , loadJS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";
import { BreadcrumbComponent } from "../breadcrumb/breadcrumb"
import { SearchComponent } from "../search/search"

  export class CatalogDesignComponent extends Component {
      static template = "e_website_design.CatalogDesignComponent";
      static components = {BreadcrumbComponent,SearchComponent};
      static props = ['back_url?','breadcrumbs?']

      setup() {
          this.state = useState({
            'designs': [],
            'category': false,
          })
          this.back_url = this.props.back_url || ''
          this.breadcrumbs = this.props.breadcrumbs || []
          this.buttonCloseFilter = useRef('buttonCloseFilter')
          this.orm = useService('orm')
          
          onWillStart(async ()=>{
              await this.searchDesigns()
          })
      }

      async searchDesigns(){
        let domain = [];
        if (this.state.category)
          domain.push(['category_id','=',this.state.category.id]);
        
        this.state.designs = await this.orm.searchRead(
          'product.design',
          domain,
          ['id','name','default_code']
        );
      }

      onSelectCategory(category){
        this.state.category = category;
        this.searchDesigns().then(()=>{
          this.buttonCloseFilter.el.click() 
        })
      }



  }

  registry.category("public_components").add("e_website_design.CatalogDesignComponent", CatalogDesignComponent);
  
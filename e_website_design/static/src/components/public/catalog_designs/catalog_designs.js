/** @odoo-module **/

import { Component , onWillStart , useState , useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
//import { loadCSS , loadJS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";
import { SearchComponent } from "../search/search"
import { removeLoader } from "../../../js/public_designs"

  export class CatalogDesignsComponent extends Component {
      static template = "e_website_design.CatalogDesignsComponent";
      static components = {SearchComponent};
      static props = ['product?','category?']

      setup() {
          this.state = useState({
            'designs': [],
            'category': false,
            'product': this.props.product,
            'category': this.props.category,
            'loadingData':false,
            'searchQuery':'',
          })
        
          this.buttonCloseFilter = useRef('buttonCloseFilter')
          this.orm = useService('orm')
          this.temp_product=this.temp_category=false
          onWillStart(async ()=>{
              await this.searchDesigns();
              removeLoader()
          })
      }

      async searchDesigns(){
        this.loadingTimeOut = setTimeout(() => {
          this.state.loadingData = true;
        }, 500);

        let domain = [];
        if (this.state.product)
          domain.push(['product_ids','=',this.state.product.id]);
        if (this.state.category)
          domain.push(['category_id','=',this.state.category.id]);
        if (this.state.searchQuery)
          domain.push(
              '|',
              ['name','ilike',this.state.searchQuery],
              ['default_code','ilike',this.state.searchQuery],
          );
        this.state.designs = await this.orm.searchRead(
          'product.design',
          domain,
          ['id','name','default_code']
        );

        if (this.loadingTimeOut)
          clearTimeout(this.loadingTimeOut)
        this.state.loadingData = false
      
      }

      onSelectCategory(category){
        this.temp_category = category;
      }

      onSelectProduct(product){
        this.temp_product = product;
      }

      applyFilter(){
        this.state.searchQuery =  ''
        this.state.product = this.temp_product
        this.state.category = this.temp_category
        this.searchDesigns()
        this.buttonCloseFilter.el.click() 
      }

      

      onSearchInput() {
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }

        this.searchTimeout = setTimeout(async () => {
            await this.searchDesigns()
        }, 500);
      }


  }

  registry.category("public_components").add("e_website_design.CatalogDesignsComponent", CatalogDesignsComponent);
  
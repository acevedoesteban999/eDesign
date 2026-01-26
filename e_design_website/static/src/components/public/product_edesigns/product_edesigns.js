/** @odoo-module **/

import { Component, onWillStart, useEffect, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
//import { loadCSS , loadJS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";
import { SearchComponent } from "../search/search"

  export class EProductDesign extends Component {
      static template = "e_design_website.EProductDesign";
      static components = { SearchComponent };
      static props = ['product?','category?','base_url']

      setup() {
          this.state = useState({
            'designs': [],
            'product': this.props.product,
            'category': this.props.category,
            'subcategory': false,
            'subcategories': false,
            'loadingData':false,
            'searchQuery':'',
          })
          this.buttonCloseFilter = useRef('buttonCloseFilter')
          this.orm = useService('orm')
          this.temp_product = this.props.product
          this.temp_category = this.props.category
          onWillStart(async ()=>{
              await this.searchDesigns();

              const loader = document.querySelector('.loader-component');
              if (loader) {
                  loader.remove();
              }
              
          })
      }

      async searchDesigns(){
        this.loadingTimeOut = setTimeout(() => {
          this.state.loadingData = true;
        }, 500);

        let domain = [];
        if (this.state.product && this.state.product.design_ids?.length)
          domain.push(['id','in',this.state.product.design_ids]);
        
        let sub_domain = true;
        if(this.state.subcategory)
          domain.push(['category_id','=',this.state.subcategory.id]);
        else if (this.state.category)
          domain.push(['category_id','=',this.state.category.id]);
        else
          sub_domain = false
        
        this.state.subcategories = await this.orm.rpc("/e_design_website/searchRead", {
          model: 'product.edesign.category',
          domain: sub_domain?[['category_id','=',this.state.subcategory.id??this.state.category.id]]:[],
          fields: ['id','name','display_name'],
          context: {'get_subcategories': true}
        });
          
          

        if (this.state.searchQuery)
          domain.push(
              '|',
              ['name','ilike',this.state.searchQuery],
              ['default_code','ilike',this.state.searchQuery],
          );
        
        this.state.designs = await this.orm.rpc("/e_design_website/searchRead", {
            model: 'product.edesign',
            domain: domain,
            fields: ['id','name','default_code'],
            context: {'get_subcategories_ids': this.state.category?true:false}
        });

        if (this.loadingTimeOut)
          clearTimeout(this.loadingTimeOut)
        this.state.loadingData = false
      
      }

      async selectSubCategory(subcategory){
        this.state.subcategory = subcategory;
        await this.searchDesigns();
      }

      async cancelSubCategory(){
        this.state.subcategory = false;
        await this.searchDesigns();
      }

      async applyFilter(){
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

  registry.category("public_components").add("e_design_website.EProductDesign", EProductDesign);
  
/** @odoo-module **/

import { Component, onMounted, onWillStart, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { SearchComponent } from "../search/search"
import { loadJS } from "@web/core/assets";

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
        })
        this.buttonCloseFilter = useRef('buttonCloseFilter')
        this.orm = useService('orm')
        this.temp_product = this.props.product
        this.temp_category = this.props.category
        onWillStart(async ()=>{
            await loadJS("/e_design_website/static/src/lib/listjs/listjs.js");
            await this.searchDesigns();

            const loader = document.querySelector('.loader-component');
            if (loader) {
                loader.remove();
            }
        })
        onMounted(()=>{
          this.listjs = new List("listjs-search-component", {
            valueNames: ['listjs-name','listjs-defaultcode']
          });
        })
    }

    async searchDesigns(reload_category = false){
      this.loadingTimeOut = setTimeout(() => {
        this.state.loadingData = true;
      }, 500);

      let domain = [];
      if (this.state.product && this.state.product.design_ids?.length)
        domain.push(['id','in',this.state.product.design_ids]);
      
      if(reload_category){
        const _category = await this.orm.rpc("/e_design_website/searchRead", {
          model: 'product.edesign.category',
          domain: [['id','=',this.state.category.id]],
          fields: ['id','display_name','subcategories_ids']
        });

        this.state.category = _category?.[0] ?? false
        
      }

      if (this.state.category){
        
        let categories = []
        if(this.state.subcategory?.id)
          categories.push(this.state.subcategory.id)
        else{
          categories.push(this.state.category.id) 
          if(this.state.category.subcategories_ids?.length)
            categories = categories.concat(this.state.category.subcategories_ids)
        }

        domain.push(['category_id','in', categories]);
      }

      
      this.state.designs = await this.orm.rpc("/e_design_website/searchRead", {
          model: 'product.edesign',
          domain: domain,
          fields: ['id','name','default_code'],
      });
      
      if(this.state.designs?.length ){
        let domain = []
        if(this.state.category?.subcategories_ids)
          domain.push(['id','in',this.state.category.subcategories_ids])
        else
          domain.push(['parent_id','=',false])
        this.state.subcategories = await this.orm.rpc("/e_design_website/searchRead", {
          model: 'product.edesign.category',
          domain: domain,
          fields: ['id','name','parent_id'],
        });
      }
      else
        this.state.subcategories = false


      if (this.loadingTimeOut)
        clearTimeout(this.loadingTimeOut)
      this.state.loadingData = false

      if(this.listjs)
        this.listjs.reIndex()
    
    }

    async selectSubCategory(subcategory){
      if(!subcategory.parent_id){
        this.state.category = subcategory;
        this.state.subcategory = false
        await this.searchDesigns(true);
      }
      else{
        this.state.subcategory = subcategory;
        await this.searchDesigns();
      }
      
    }

    async cancelSubCategory(){
      this.state.subcategory = false;
      await this.searchDesigns();
    }

    async cancelProduct(){
      this.state.product = false
      await this.searchDesigns();
    }

    async cancelCategory(){
      this.state.category = false
      await this.searchDesigns();
    }

    async applyFilter(){
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
  
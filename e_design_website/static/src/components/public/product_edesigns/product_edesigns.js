/** @odoo-module **/

import { Component, onWillStart, useEffect, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
//import { loadCSS , loadJS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";
import { SearchComponent } from "../search/search"
import { removeLoader } from "../../../js/public_designs"

  export class EProductDesign extends Component {
      static template = "e_design_website.EProductDesign";
      static components = { SearchComponent };
      static props = ['product?','category?']

      setup() {
          this.state = useState({
            'designs': [],
            'product': this.props.product,
            'category': this.props.category,
            'loadingData':false,
            'searchQuery':'',
          })
          this.extraHref = this.props.product?('pid='+this.props.product.id):this.props.category?('cid='+this.props.category.id):''
          this.buttonCloseFilter = useRef('buttonCloseFilter')
          this.orm = useService('orm')
          this.temp_product = this.temp_category = false
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
        
        if (this.state.product && this.state.product.design_ids?.length)
          domain.push(['id','in',this.state.product.design_ids]);
        if (this.state.category)
          domain.push(['category_id','=',this.state.category.id]);
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
        });

        if (this.loadingTimeOut)
          clearTimeout(this.loadingTimeOut)
        this.state.loadingData = false
      
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
  
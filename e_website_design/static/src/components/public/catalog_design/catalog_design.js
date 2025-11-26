/** @odoo-module **/

import { Component , onWillStart , onMounted , useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { loadCSS , loadJS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";

  export class CatalogDesignComponent extends Component {
      static template = "e_design.DesignComponent";
      static components = {};
      static props = {};

      setup() {
        // console.log("A")
        // this.state = useState({
        //   'products':[],
        
        // });
        // this.orm = useService('orm');
  
        // onWillStart(async () => {
        //   await this.getData();
        //   await loadCSS('/e_design/static/src/library/lightgallery/lightgallery.css');
        //   await loadJS('/e_design/static/src/library/lightgallery/lightgallery.js')
        // });
  
        // onMounted(() => {
        //   lightGallery(document.getElementById('animated-thumbnails'), {
        //     selector: '.lg-item',
        //     thumbnail: true,
        //     animateThumb: true,
        //     showThumbByDefault: false
        //   });
        
          
        // });
      }

    //   async getData(){
    //     this.state.products = await this.orm.searchRead(
    //       'product.template',
    //       [
    //         ['sublimation_ok','=',true],
    //         ['product_tmpl_sublimation_id','!=',false],
    //       ],
    //       ['name','id','attachment_ids']
    //     )
    //   }

    //   getRandomChildren(products, count = 3) {
    //     if (!products || products.length === 0) {
    //         return Array(null);
    //     }
    //     const shuffled = [...products].sort(() => 0.5 - Math.random());
    //     const selected = shuffled.slice(0, Math.min(count, products.length));
    //     return selected;
    // }
  }

  registry.category("public_components").add("e_design.CatalogDesignComponent", CatalogDesignComponent);
  
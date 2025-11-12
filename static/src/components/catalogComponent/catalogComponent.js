/** @odoo-module **/

import { Component , onWillStart , onMounted , useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { loadCSS , loadJS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";


export class CatalogComponent extends Component {
    static template = "e_sublimation.CatalogComponent";
    static components = {};
    static props = {};

    setup() {
      this.state = useState({'catalogs':[]});
      this.orm = useService('orm');

      onWillStart(async () => {
        await this.getData();
        await loadCSS('https://cdn.jsdelivr.net/npm/swiper@12/swiper-bundle.min.css');
        await loadJS('https://cdn.jsdelivr.net/npm/swiper@12/swiper-bundle.min.js')
      });
      
      onMounted(() => {
        this.swiper = new Swiper('.swiper', {
          loop: this.state.catalogs.length > 1,
          speed: 400,
          spaceBetween: 100,
          pagination: { el: '.swiper-pagination' },
          navigation: { nextEl: '.swiper-button-next', prevEl: '.swiper-button-prev' },
          scrollbar: { el: '.swiper-scrollbar' },
        });

      });

    }

    async getData(){
      this.state.catalogs = await this.orm.searchRead(
        'e_sublimation.category',
        [],
        ['name','id']
      )
       
    }
}

registry.category("public_components").add("e_sublimation.catalogComponent", CatalogComponent);
  
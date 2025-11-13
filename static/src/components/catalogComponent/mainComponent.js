/** @odoo-module **/

import { Component , onWillStart , onMounted , useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { loadCSS , loadJS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";


export class MainComponent extends Component {
    static template = "e_sublimation.MainComponent";
    static components = {};
    static props = {};

    setup() {
      this.state = useState({
        'categories':[],
        'products':[],
      
      });
      this.orm = useService('orm');

      onWillStart(async () => {
        await this.getData();
        await loadCSS('https://cdn.jsdelivr.net/npm/swiper@12/swiper-bundle.min.css');
        await loadJS('https://cdn.jsdelivr.net/npm/swiper@12/swiper-bundle.min.js')
      });

      onMounted(() => {
        this.swiper = new Swiper('.swiper', {
          loop: this.state.categories.length > 1,
          speed: 400,
          autoplay: {
            delay: 3000,
            disableOnInteraction: false, 
            pauseOnMouseEnter: true, 
          },
          pagination: { el: '.swiper-pagination' },
          navigation: { nextEl: '.swiper-button-next', prevEl: '.swiper-button-prev' },
          scrollbar: { el: '.swiper-scrollbar' },
        });

        this.swiper_products = new Swiper('.swiper-products', {
          loop: this.state.products.length > 1,
            speed: 400,
            autoplay: {
                delay: 5000,
                disableOnInteraction: false,
                pauseOnMouseEnter: true,
            },
            navigation: {
                nextEl: '.swiper-button-next-products',
                prevEl: '.swiper-button-prev-products',
            },
            pagination: {
                el: '.swiper-pagination-products',
                clickable: true,
            },
            watchOverflow: true,
            observer: true,
            observeParents: true,
            breakpoints: {
                320: {
                    slidesPerView: 1,
                },
                768: {
                    slidesPerView: 1,
                }
            }
        });
        
      });

    }

    async getData(){
      this.state.categories = await this.orm.searchRead(
        'e_sublimation.category',
        [],
        ['name','id']
      )
      this.state.products = await this.orm.searchRead(
        'product.template',
        [
          ['product_tmpl_sublimation_id','=',false],
          ['sublimation_ok','=',true],
        ],  
        ['name','id','product_childs_sublimation_ids']
      )
       
    }

    getRandomChildren(products, count = 3) {
      if (!products || products.length === 0) {
          return Array(count).fill(null);
      }
      const shuffled = [...products].sort(() => 0.5 - Math.random());
      const selected = shuffled.slice(0, Math.min(count, products.length));
      while (selected.length < count) {
          selected.push(null);
      }
      return selected;
  }
}

registry.category("public_components").add("e_sublimation.MainComponent", MainComponent);
  
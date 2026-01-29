/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { loadJS } from "@web/core/assets";

publicWidget.registry.CategorySearch = publicWidget.Widget.extend({
    selector: '#searchable-list',
    
    async willStart() {
        await loadJS("/e_design_website/static/src/lib/simple_search/simple_search.js");
    },
    
    start: function() {
        this._super.apply(this, arguments);
        
        this.search = new SimpleSearch('#searchable-list', {
            searchInput: '#searchable-input',
            markSelector: '[data-search-mark]',
            containerSelector: '[data-search-container]',
            groupSelector: '[data-search-group]',
            hiddenClass: 'd-none',
            emptyMessage: this.el.dataset.emptyMessage ?? 'No items found',
            emptyClass: this.el.dataset.emptyClass ?? 'alert alert-info text-center my-4',
            minChars: 1,
        });
    },
    
    destroy: function() {
        if (this.search) {
            this.search.destroy();
        }
        this._super.apply(this, arguments);
    }
});
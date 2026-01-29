/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.DivHref = publicWidget.Widget.extend({
    selector: '.div-href',
    events: {
        'click': '_onClick',
    },
    
    _onClick: function (ev) {
        
        const href = this.el.dataset.widgetHref;
        const stopPropagation = this.el.dataset.widgetStopPropagation === '1';
        
        if (stopPropagation) {
            ev.stopPropagation();
        }
        
        if (href) {
            window.location.href = href;
        }
    },
});
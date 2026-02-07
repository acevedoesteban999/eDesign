/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState } from "@odoo/owl";

export class ImportPreview extends Component {
    static template = "e_design_import.ImportPreview";
    static props = {
        ...standardFieldProps,
    };
    
    setup() {
        this.state = useState({
            expanded: new Set(),
        });
    }

    get previewData() {
        const value = this.props.record.data[this.props.name];
        return value || {
            categories: [],
            products: [],
            designs: []
        };
    }

    get stats() {
        const data = this.previewData;
        let categories = 0, subcategories = 0, products = 0, designs = 0;
        let newCategories = 0, newSubcategories = 0, newProducts = 0, newDesigns = 0;

        const countCategory = (cat) => {
            categories++;
            if (!cat.id) newCategories++;
            
            (cat.subcategories || []).forEach(sub => {
                subcategories++;
                if (!sub.id) newSubcategories++;
                
                (sub.products || []).forEach(prod => {
                    products++;
                    if (!prod.id) newProducts++;
                    
                    (prod.designs || []).forEach(des => {
                        designs++;
                        if (!des.id) newDesigns++;
                    });
                });
                
                (sub.designs || []).forEach(des => {
                    designs++;
                    if (!des.id) newDesigns++;
                });
            });
            
            (cat.products || []).forEach(prod => {
                products++;
                if (!prod.id) newProducts++;
                
                (prod.designs || []).forEach(des => {
                    designs++;
                    if (!des.id) newDesigns++;
                });
            });
            
            (cat.designs || []).forEach(des => {
                designs++;
                if (!des.id) newDesigns++;
            });
        };

        (data.categories || []).forEach(countCategory);
        
        (data.products || []).forEach(prod => {
            products++;
            if (!prod.id) newProducts++;
            
            (prod.designs || []).forEach(des => {
                designs++;
                if (!des.id) newDesigns++;
            });
        });
        
        (data.designs || []).forEach(des => {
            designs++;
            if (!des.id) newDesigns++;
        });

        return {
            categories,
            subcategories,
            products,
            designs,
            newCategories,
            newSubcategories,
            newProducts,
            newDesigns
        };
    }

    getAllCodes() {
        const codes = new Set();
        const data = this.previewData;

        const collectCodes = (cat) => {
            codes.add(cat.code);
            (cat.subcategories || []).forEach(sub => {
                codes.add(sub.code);
                (sub.products || []).forEach(prod => codes.add(prod.code));
            });
            (cat.products || []).forEach(prod => codes.add(prod.code));
        };

        (data.categories || []).forEach(collectCodes);
        (data.products || []).forEach(prod => codes.add(prod.code));

        return codes;
    }

    expandAll() {
        const allCodes = this.getAllCodes();
        this.state.expanded.clear();
        allCodes.forEach(code => this.state.expanded.add(code));
    }

    collapseAll() {
        this.state.expanded.clear();
    }

    toggleExpand(code) {
        if (this.state.expanded.has(code)) {
            this.state.expanded.delete(code);
        } else {
            this.state.expanded.add(code);
        }
    }

    isExpanded(code) {
        return this.state.expanded.has(code);
    }
}

export const importPreview = {
    component: ImportPreview,
};

registry.category("fields").add("import_preview", importPreview);
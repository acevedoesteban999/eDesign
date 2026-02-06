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

    get data() {
        const value = this.props.record.data[this.props.name];
        return value || {
            categories: [],
            subcategories: [],
            designs: [],
            products: [],
            existing: {
                categories: [],
                subcategories: [],
                designs: [],
                products: []
            }
        };
    }

    get stats() {
        const data = this.data;
        const existing = data.existing || {};
        const existingCatCodes = new Set((existing.categories || []).map(c => c.code));
        const existingSubCodes = new Set((existing.subcategories || []).map(s => s.code));
        const existingDesCodes = new Set((existing.designs || []).map(d => d.code));
        const existingProdCodes = new Set((existing.products || []).map(p => p.code));
        
        return {
            categories: data.categories?.length || 0,
            subcategories: data.subcategories?.length || 0,
            designs: data.designs?.length || 0,
            products: data.products?.length || 0,
            newCategories: (data.categories || []).filter(c => !existingCatCodes.has(c.code)).length,
            newSubcategories: (data.subcategories || []).filter(s => !existingSubCodes.has(s.code)).length,
            newDesigns: (data.designs || []).filter(d => !existingDesCodes.has(d.code)).length,
            newProducts: (data.products || []).filter(p => !existingProdCodes.has(p.code)).length
        };
    }

    get categories() {
        const data = this.data;
        const existingCats = new Set((data.existing?.categories || []).map(c => c.code));
        
        return (data.categories || []).map(cat => ({
            ...cat,
            isNew: !existingCats.has(cat.code),
            subcategories: this.getSubcategories(cat.code),
            designs: this.getDesigns(cat.code)
        }));
    }

    getSubcategories(parentCode) {
        const data = this.data;
        const existingSubs = new Set((data.existing?.subcategories || []).map(s => s.code));
        
        return (data.subcategories || [])
            .filter(sub => sub.parent_code === parentCode)
            .map(sub => ({
                ...sub,
                isNew: !existingSubs.has(sub.code),
                designs: this.getDesigns(sub.code)
            }));
    }

    getDesigns(categoryCode) {
        const data = this.data;
        const existingDes = new Set((data.existing?.designs || []).map(d => d.code));
        
        return (data.designs || [])
            .filter(design => design.category_code === categoryCode)
            .map(design => ({
                ...design,
                isNew: !existingDes.has(design.code)
            }));
    }

    // Obtener todos los códigos posibles para expandir/colapsar
    getAllCodes() {
        const codes = new Set();
        const categories = this.categories;
        
        categories.forEach(cat => {
            codes.add(cat.code);
            (cat.subcategories || []).forEach(sub => {
                codes.add(sub.code);
            });
        });
        
        return codes;
    }

    expandAll() {
        const allCodes = this.getAllCodes();
        // Limpiar y agregar todos
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
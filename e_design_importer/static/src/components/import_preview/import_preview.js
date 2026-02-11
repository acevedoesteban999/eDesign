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
            disabled : new Set(),
        });
        this.errors = new Set()
        this.getAllErrors()
        this.state.disabled = this.errors
    }

    get orderedCounters() {
        const order = ['categories', 'subcategories', 'products', 'designs'];
        return order.map(key => this.counters[key]);
    }

    get previewData() {
        return this.props.record.data[this.props.name].preview_data;
    }

    get counters() {
        return this.props.record.data[this.props.name].counters;
    }

    getAllErrors(){
        let errors = new Set()
        const data = this.previewData;

        const nodeError = (node)=>{
            if (node.error)
                errors.add(node.code)
        }

        const errorDesigns = (des)=>{
            nodeError(des)
        }
        const errorProducts = (prod)=>{
            nodeError(prod);
            (prod.designs || []).forEach(errorDesigns);
        }
        const errorCategories = (cat) => {
            nodeError(cat);
            (cat.subcategories || []).forEach(sub => {
                nodeError(sub);
                (sub.products || []).forEach(errorProducts);
                (sub.designs || []).forEach(errorDesigns);
            });
            (cat.products || []).forEach(errorProducts);
            (cat.designs || []).forEach(errorDesigns);
        }

        (data.categories || []).forEach(errorCategories);
        (data.products || []).forEach(errorProducts);
        (data.designs || []).forEach(errorDesigns);

        this.errors = errors
    }

    getAllExpandCodes() {
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
        const allCodes = this.getAllExpandCodes();
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

    toggleDisabled(code) {
        if (this.state.disabled.has(code)) {
            this.state.disabled.delete(code);
        } else {
            this.state.disabled.add(code);
        }
    }

    isExpanded(code) {
        return this.state.expanded.has(code);
    }

    isDisabled(code) {
        return this.state.disabled.has(code);
    }

    isError(code) {
        return this.errors.has(code);
    }
}

export const importPreview = {
    component: ImportPreview,
};

registry.category("fields").add("import_preview", importPreview);
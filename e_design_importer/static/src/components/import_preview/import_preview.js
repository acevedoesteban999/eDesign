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
        return this.props.record.data[this.props.name].preview_data;
    }

    get counters() {
        return this.props.record.data[this.props.name].counters;
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
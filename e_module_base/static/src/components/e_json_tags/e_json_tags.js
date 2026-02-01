
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

export class EJsonTagsField extends Component {
    static template = "e_module_translate.EJsonTagsField";
    static props = { ...standardFieldProps };

    get tags() {
        const raw = this.props.record.data[this.props.name];
        if (!raw) return [];
        try {
            return Array.isArray(raw) ? raw : [];
        } catch {
            return [];
        }
    }

    colorFor(text) {
        const colors = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];
        let hash = 0;
        for (let i = 0; i < text.length; i++) {
            hash = (hash << 5) - hash + text.charCodeAt(i);
            hash |= 0;
        }
        return colors[Math.abs(hash) % colors.length];
    }
}

const eJsonTagsField = {
    displayName: "EJsonTags",
    component: EJsonTagsField,
    supportedTypes: ["*"],
    extractProps: ({ attrs }) => ({
        name: attrs.name,
    }),
    
};


registry.category("fields").add("ejson_tags", eJsonTagsField);
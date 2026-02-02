/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { AutoComplete } from "@web/core/autocomplete/autocomplete";
import { Component, useState } from "@odoo/owl";

export class EJsonTagsField extends Component {
    static template = "e_module_translate.EJsonTagsField";
    static components = { AutoComplete };
    
    static props = {
        ...standardFieldProps,
        options_js_field: { type: String, optional: true }, 
    };

    setup() {
        this.state = useState({
            inputValue: "",
        });
    }

    get tags() {
        const value = this.props.record.data[this.props.name];
        return Array.isArray(value) ? value : [];
    }

    get allOptions() {
        if (!this.props.options_js_field) return [];
        const optionsData = this.props.record.data[this.props.options_js_field];
        return Array.isArray(optionsData) ? optionsData : [];
    }

    get availableOptions() {
        const selectedNames = new Set(this.tags.map(t => t.name));
        return this.allOptions.filter(opt => !selectedNames.has(opt.name));
    }

    get autoCompleteSources() {
        const options = this.availableOptions
            .filter(opt => opt.name.toLowerCase().includes(this.state.inputValue.toLowerCase()))
            .map(opt => ({
                label: opt.name,
                value: opt.name,
                name: opt.name
            }));
            
        return [{
            options: options
        }];
    }

    colorFor(text) {
        const colors = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];
        let hash = 0;
        for (let i = 0; i < text.length; i++) {
            hash = ((hash << 5) - hash) + text.charCodeAt(i);
            hash |= 0;
        }
        return colors[Math.abs(hash) % colors.length];
    }

    removeTag(tagToRemove) {
        const newTags = this.tags.filter(t => t.name !== tagToRemove.name);
        this.props.record.update({ [this.props.name]: newTags });
    }

    onAutoCompleteSelect(option) {
        const newTags = [...this.tags, { name: option.value }];
        this.props.record.update({ [this.props.name]: newTags });
        this.state.inputValue = "";
    }

    onAutoCompleteInput(ev) {
        this.state.inputValue = ev.inputValue;
    }
}

export const eJsonTagsField = {
    component: EJsonTagsField,
    displayName: "EJsonTags",
    supportedTypes: ["json", "char"],
    extractProps: ({ options }) => ({
        options_js_field: options?.options_js_field,
    }),
};

registry.category("fields").add("ejson_tags", eJsonTagsField);
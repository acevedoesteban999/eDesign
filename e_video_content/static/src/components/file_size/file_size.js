/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

export class FileSizeField extends Component {
    static template = "e_video_content.FileSizeField";
    static props = { ...standardFieldProps };

    get formattedSize() {
        try{
            const bytes = parseInt(this.props.record.data[this.props.name]);
        
            if (!bytes || bytes === 0) return "0";
            if (typeof bytes !== 'number') return "0";

            const units = ['B', 'KB', 'MB', 'GB'];
            const k = 1024;
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            
            const unitIndex = Math.min(i, units.length - 1);
            
            const size = parseFloat((bytes / Math.pow(k, unitIndex)).toFixed(2));
            
            return `${size} ${units[unitIndex]}`;
        }catch(e){
            return '-'
        }
    }

    get tooltip() {
        const bytes = this.props.record.data[this.props.name];
        return `${bytes?.toLocaleString() || 0} bytes`;
    }
}

export const fileSizeField = {
    component: FileSizeField,
    supportedTypes: ["integer", "float"],
    displayName: "File Size",
};

registry.category("fields").add("file_size", fileSizeField);
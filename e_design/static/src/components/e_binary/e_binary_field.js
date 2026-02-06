import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { isBinarySize } from "@web/core/utils/binary";
import { download } from "@web/core/network/download";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { FileUploader } from "@web/views/fields/file_handler";
import { _t } from "@web/core/l10n/translation";

import { Component, useState, onMounted } from "@odoo/owl";

export class EBinaryField extends Component {
    static template = "e_design.EBinaryField";
    static components = { FileUploader };
    static props = {
        ...standardFieldProps,
        acceptedFileExtensions: { type: String, optional: true },
        fileNameField: { type: String, optional: true },
    };
    static defaultProps = {
        acceptedFileExtensions: "*",
    };

    setup() {
        this.notification = useService("notification");
        this.orm = useService("orm");
        
        this.state = useState({
            fileInfo: {
                name: '', 
                size: '', 
                format: '',
            }
        });
        this.cached_filename = ''
        onMounted(() => {
            this.updateFileInfo();
        });
    }

    updateFileInfo() {
        const data = this.props.record.data[this.props.name];
        const name = this.props.fileNameField 
            ? this.props.record.data[this.props.fileNameField] 
            : '';
        
        if (!data) {
            this.state.fileInfo = { name: '', size: '', format: '' };
            return;
        }

        const size = this.calculateSizeFromBase64(data);
        const format = this.getFormatFromName(name);
        
        this.state.fileInfo = {
            name: name || this.cached_filename,
            size: this.formatFileSize(size),
            format: format,
        };
    }

    calculateSizeFromBase64(base64String) {
        if (!base64String || typeof base64String !== 'string') return 0;
        
        const base64Data = base64String.includes(',') 
            ? base64String.split(',')[1] 
            : base64String;
            
        if (!base64Data) return 0;
        
        let padding = 0;
        if (base64Data.endsWith('==')) padding = 2;
        else if (base64Data.endsWith('=')) padding = 1;
        
        return (base64Data.length * 3 / 4) - padding;
    }

    getFormatFromName(filename) {
        if (!filename) return '';
        const parts = filename.split('.');
        return parts.length > 1 ? parts.pop().toLowerCase() : '';
    }

    async update({ data, name }) {
        if (!data) {
            const changes = { [this.props.name]: false };
            if (this.props.fileNameField) {
                changes[this.props.fileNameField] = false;
            }
            await this.props.record.update(changes);
            this.state.fileInfo = { name: '', size: '', format: '' };
            return;
        }

        const changes = { [this.props.name]: data };
        if (this.props.fileNameField && name) {
            changes[this.props.fileNameField] = name;
        }

        await this.props.record.update(changes);

        this.cached_filename = name
        // if (this.props.record.isDirty) {
        //     await this.props.record.save();
        // }

        const size = this.calculateSizeFromBase64(data);
        const format = this.getFormatFromName(name);
        this.state.fileInfo = {
            name: name,
            size: this.formatFileSize(size),
            format: format,
        };
    }

    formatFileSize(bytes) {
        if (!bytes || bytes === 0) return '0';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.min(Math.floor(Math.log(bytes) / Math.log(k)), sizes.length - 1);
        const value = bytes / Math.pow(k, i);
        return i === 0 ? Math.round(value) + ' ' + sizes[i] : value.toFixed(2) + ' ' + sizes[i];
    }

    getDownloadData() {
        return {
            model: this.props.record.resModel,
            id: this.props.record.resId,
            field: this.props.name,
            filename_field: this.props.fileNameField,
            filename: this.state.fileInfo.name || this.cached_filename,
            download: true,
            data: isBinarySize(this.props.record.data[this.props.name])
                ? null
                : this.props.record.data[this.props.name],
        };
    }

    getFileIconClass(format) {
        const map = {
            'pdf': 'fa-file-pdf-o',
            'jpg': 'fa-file-image-o', 'jpeg': 'fa-file-image-o', 'png': 'fa-file-image-o', 
            'gif': 'fa-file-image-o', 'webp': 'fa-file-image-o',
            'doc': 'fa-file-word-o', 'docx': 'fa-file-word-o',
            'xls': 'fa-file-excel-o', 'xlsx': 'fa-file-excel-o', 'csv': 'fa-file-excel-o',
            'txt': 'fa-file-text-o',
            'zip': 'fa-file-archive-o', 'rar': 'fa-file-archive-o',
            'mp4': 'fa-file-video-o', 'mp3': 'fa-file-audio-o',
        };
        return map[format] || 'fa-file-o';
    }

    async onFileDownload() {
        await download({
            data: this.getDownloadData(),
            url: "/web/content",
        });
    }
}

export const eBinaryField = {
    component: EBinaryField,
    displayName: _t("EFile"),
    supportedOptions: [
        {
            label: _t("Accepted file extensions"),
            name: "accepted_file_extensions",
            type: "string",
        },
    ],
    supportedTypes: ["binary"],
    extractProps: ({ attrs, options }) => ({
        acceptedFileExtensions: options.accepted_file_extensions,
        fileNameField: attrs.filename,
    }),
};

registry.category("fields").add("e_binary_field", eBinaryField);
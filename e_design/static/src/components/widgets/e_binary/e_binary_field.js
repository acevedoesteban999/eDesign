import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { isBinarySize, toBase64Length } from "@web/core/utils/binary";
import { download } from "@web/core/network/download";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { FileUploader } from "@web/views/fields/file_handler";
import { _t } from "@web/core/l10n/translation";

import { Component , useState } from "@odoo/owl";

export const MAX_FILENAME_SIZE_BYTES = 0xFF;

export class EBinaryField extends Component {
    static template = "e_design.EBinaryField";
    static components = {
        FileUploader,
    };
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
        this.state = useState({
            'fileInfo':{
                'name':'', 
                'size':'', 
                'format':'',
            }
        })
        this.GetAttachmentInfo();
    }

    get fileName() {
        return (
            this.props.record.data[this.props.fileNameField] ||
            this.props.record.data[this.props.name] ||
            ""
        ).slice(0, toBase64Length(MAX_FILENAME_SIZE_BYTES));
    }

    update({ data, name }) {
        const changes = { [this.props.name]: data || false };
        
        var res =  this.props.record.update(changes);
        this.GetAttachmentInfo(name)
        return res
    }

    getDownloadData() {
        return {
            model: this.props.record.resModel,
            id: this.props.record.resId,
            field: this.props.name,
            filename_field: this.fileName,
            filename: this.state.fileInfo.name || "",
            download: true,
            data: isBinarySize(this.props.record.data[this.props.name])
                ? null
                : this.props.record.data[this.props.name],
        };
    }
    formatFileSize(bytes) {
        if (!bytes || bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'K', 'M'];
        
        const i = Math.min(Math.floor(Math.log(bytes) / Math.log(k)), 2);
        
        const value = bytes / Math.pow(k, i);
        
        if (i === 0) {
            return Math.round(value) + ' ' + sizes[i];
        } else {
            return value.toFixed(i === 1 ? 1 : 2) + sizes[i];
        }
    }
    
    async GetAttachmentInfo(name) {
        const record = this.props.record;
        const resId = record.resId;
        
        if (!resId) 
            return null;

        let attachment = await this.env.services.orm.searchRead(
            'ir.attachment',
            [['id', '=', resId]],
            ['name','file_size','mimetype'],
        );
        attachment = attachment ? attachment[0] : false;
        if (name){
            await this.env.services.orm.write(
                'ir.attachment',
                [resId],
                {'name':name},
            )
        }
        if (attachment){
            this.state.fileInfo = {
                'name':attachment.name,
                'size':this.formatFileSize(attachment.file_size),
                'format': attachment.mimetype?attachment.mimetype.split('/').pop().toLowerCase():'',
            }
        }
        
    }

    getFileIconClass(format) {
        if (!format) return 'fa-file-o';
        
        const formatMap = {
            'pdf': 'fa-file-pdf-o',
            'jpg': 'fa-file-image-o', 
            'jpeg': 'fa-file-image-o', 
            'png': 'fa-file-image-o', 
            'gif': 'fa-file-image-o',
            'doc': 'fa-file-word-o', 
            'docx': 'fa-file-word-o',
            'xls': 'fa-file-excel-o', 
            'xlsx': 'fa-file-excel-o', 
            'csv': 'fa-file-csv',
            'txt':'fa-file-text-o',
            'zip': 'fa-file-archive-o', 
            'rar': 'fa-file-archive-o', 
            '7z': 'fa-file-archive-o',
            'mp4': 'fa-file-video-o', 
            'avi': 'fa-file-video-o',
            'mp3': 'fa-file-audio-o', 
            'wav': 'fa-file-audio-o',
        };
        
        const ext = format.toLowerCase().replace('.', '');
        return formatMap[ext] || 'fa-file-o';
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

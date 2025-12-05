import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { FileInput } from "@web/core/file_input/file_input";
import { useX2ManyCrud } from "@web/views/fields/relational_utils";
import { Component, onMounted, onWillStart } from "@odoo/owl";
import { loadCSS , loadJS } from "@web/core/assets";

const standardFieldProps = {
    id: { type: String, optional: true },
    name: { type: String },
    readonly: { type: Boolean, optional: true },
    record: { type: Object },
};

export class E_Design_Many2ManyImage extends Component {
    static template = "e_design.Many2ManyImage";
    static components = {
        FileInput,
    };
    static props = {
        ...standardFieldProps,
        acceptedFileExtensions: { type: String, optional: true },
        className: { type: String, optional: true },
        numberOfFiles: { type: Number, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.operations = useX2ManyCrud(() => this.props.record.data[this.props.name], true);
        onWillStart(async () => {
            await loadCSS('/e_design/static/src/library/fancybox/fancybox.css');
            await loadJS('/e_design/static/src/library/fancybox/fancybox.js')
        });
        onMounted(() => {
            Fancybox.bind("[data-fancybox]", {
                placeFocusBack: false,
                
                Hash: false,
                
                dragToClose: true,
                wheel: "zoom",
                closeButton: "top",
                
                on: {
                    "init": () => console.log("Fancybox iniciado"),
                    "destroy": () => console.log("Fancybox cerrado"),
                },
            });
        });
        
    }

    get uploadText() {
        return this.props.record.fields[this.props.name].string;
    }
    get files() {
        return this.props.record.data[this.props.name].records.map((record) => {
            return {
                ...record.data,
                id: record.resId,
            };
        });
    }

    getUrl(id) {
        return "/web/content/" + id + "?download=true";
    }

    getExtension(file) {
        return file.name.replace(/^.*\./, "");
    }
    toogleFullscreen(){
        this.img.el.class.toogle('fullscreen')
    }
    async onFileUploaded(files) {
        for (const file of files) {
            if (file.error) {
                return this.notification.add(file.error, {
                    title: _t("Uploading error"),
                    type: "danger",
                });
            }
            await this.operations.saveRecord([file.id]);
        }
    }

    async onFileRemove(deleteId) {
        const record = this.props.record.data[this.props.name].records.find(
            (record) => record.resId === deleteId
        );
        this.operations.removeRecord(record);
    }
}

export const many2ManyImage = {
    component: E_Design_Many2ManyImage,
    supportedOptions: [
        {
            label: _t("Accepted file extensions"),
            name: "accepted_file_extensions",
            type: "string",
        },
        {
            label: _t("Number of files"),
            name: "number_of_files",
            type: "integer",
        },
    ],
    supportedTypes: ["many2many"],
    isEmpty: () => false,
    relatedFields: [
        { name: "name", type: "char" },
        { name: "mimetype", type: "char" },
    ],
    extractProps: ({ attrs, options }) => ({
        acceptedFileExtensions: options.accepted_file_extensions,
        className: attrs.class,
        numberOfFiles: options.number_of_files,
    }),
};

registry.category("fields").add("many2many_image", many2ManyImage);

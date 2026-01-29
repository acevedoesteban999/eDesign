/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

export class EDesignProduct extends Component {
    static template = "e_design.eDesignProductTemplate";
    static props = { ...standardFieldProps };

    setup() {
        this.state = useState({
            designs: [],
            search: "",
        });

        this.orm = useService("orm");
        this.action = useService("action");
        this.dialog = useService("dialog");

        onWillStart(async () => {
            await this.getDesigns();
        });
    }

    async getDesigns(reload = false) {
        let designIds = this.props.record.data[this.props.name]._currentIds;
        if (reload) {
            const readRes = await this.orm.call(
                "product.template",
                "read",
                [[this.props.record.resId], ["design_ids"]]
            );
            designIds = readRes[0]?.design_ids || [];
        }
        this.state.designs = await this.orm.call(
            "product.edesign",
            "read",
            [designIds, ["id", "name", "default_code", "image","category_id"]]
        );
    }

    get filteredDesigns() {
        const s = this.state.search.toLowerCase();
        return this.state.designs.filter(d =>
            d.name.toLowerCase().includes(s) ||
            (d.default_code || "").toLowerCase().includes(s)
        );
    } 

    _doDesignAction(method, context) {
        return this.action.doAction(
            this.orm.call(
              "product.edesign",
              "get_design_action", 
              [method, context]),
            {
                onClose: async () => {
                    await this.getDesigns(true);
                    await this.props.record.model.load();
                },
            }
        );
    }

    createDesign() {
        return this._doDesignAction("create", {
            default_product_id: this.props.record.data.id,
        });
    }

    linkDesign() {
        return this._doDesignAction("link", {
            default_product_id: this.props.record.data.id,
        });
    }

    openDesign(id) {
        return this._doDesignAction("open", {
            product_design_id: id,
        });
    }

    unlinkDesign(design) {
        this.dialog.add(ConfirmationDialog, {
            title: "Confirm",
            body: `Are you sure you want to unlink the design "${design.name}"?`,
            confirm: async () => {
                await this.orm.call(
                    "product.template",
                    "unlink_design", 
                    [[this.props.record.resId],design.id]);
                await this.getDesigns(true);
                await this.props.record.model.load();
            },
            cancel: () => {},
        });
    }
}

const eDesignProduct = {
  displayName: 'eDesign Product Template',
  component: EDesignProduct,
  supportedTypes: ['many2many'],
  extractProps: ({ attrs }) => ({
    name: attrs.name,
  }),
};

registry.category("fields").add("edesign_product_template", eDesignProduct);

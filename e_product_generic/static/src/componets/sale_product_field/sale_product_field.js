/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { SaleOrderLineProductField } from "@sale/js/sale_product_field";
import { GenericConfiguratorDialog } from "../generic_configurator_dialog/generic_configurator_dialog";

patch(SaleOrderLineProductField.prototype, {
    get isGeneric() {
        return this.props.record.data.has_generic_product;
    },
    get hasConfigurationButton() {
        return super.hasConfigurationButton || this.isGeneric;
    },
    async _onProductUpdate() {
        if(this.isGeneric)
            this._openGenericConfiguration()
        return super._onProductUpdate()
    },
    _editLineConfiguration() {
        if(this.isGeneric)
            this._openGenericConfiguration(true)
        return super._onProductUpdate()
    }, 
    async _openGenericConfiguration(edit=false){
        const saleOrder = this.props.record.model.root.data;
        const genericData = {
            generic_bill_material_data: edit?this.props.record.data.generic_bill_material_data:[],
            finalCost: edit?this.props.record.data.price_unit:0
        }
        this.dialog.add(GenericConfiguratorDialog, {
            product_template_id: this.props.record.data.product_template_id[0],
            ...genericData,
            save: async (vals)=>{
                await this.props.record.update({
                    price_unit: vals.finalCost,
                    generic_bill_material_data: vals.generic_bill_material_data,
                })
            },
            discard: () => {
                saleOrder.order_line.delete(this.props.record);
            },
        });
    },
});
/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { SaleOrderLineProductField } from "@sale/js/sale_product_field";
import { GenericConfiguratorDialog } from "../generic_configurator_dialog/generic_configurator_dialog";
import { uuid } from "@web/views/utils";

patch(SaleOrderLineProductField.prototype, {
    get isGeneric() {
        return this.props.record.data.has_generic_product;
    },
    get hasConfigurationButton() {
        return super.hasConfigurationButton || this.isGeneric;
    },
    async onEditConfiguration() {
        if(await this.isGeneric )
            this._openGenericConfiguration(true)
        else
            super.onEditConfiguration()
    },
    async _onProductTemplateUpdate(){
        if( this.isGeneric ){
            const result = await this.orm.call(
                'product.template',
                'get_single_product_variant',
                [this.props.record.data.product_template_id[0]],
                {
                    context: this.context,
                }
            );
       
            if (result && result.product_id && this.props.record.data.product_id != result.product_id.id) {
                await this.props.record.update({
                    product_id: [result.product_id, result.product_name],
                });
                await this._openGenericConfiguration()
            }
        }
        else
            await super._onProductTemplateUpdate()
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
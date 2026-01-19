/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { SaleOrderLineProductField } from "@sale/js/sale_product_field";
import { DinamicConfiguratorDialog } from "../dinamic_configurator_dialog/dinamic_configurator_dialog";

patch(SaleOrderLineProductField.prototype, {
    setup(){
        super.setup();
        this._to_edit = false;
    },
    get isDinamic() {
        return this.props.record.data.is_dinamic_mto;
    },
    get hasConfigurationButton() {
        return super.hasConfigurationButton || this.isDinamic;
    },
    async _onProductUpdate() {
        if(this.isDinamic)
            if(this.isConfigurableTemplate && this._to_edit){
                this._openDinamicConfiguration(true)
                this._to_edit = false
            }
            else
                this._openDinamicConfiguration()
        return super._onProductUpdate()
    },
    onEditConfiguration() {
        if(this.isDinamic){
            if(!this.isConfigurableTemplate)
                this._openDinamicConfiguration(true)
            else
                this._to_edit = true
        }
        return super.onEditConfiguration()
    }, 

    async _openDinamicConfiguration(edit=false){
        const saleOrder = this.props.record.model.root.data;
        const dinamicData = {
            dinamic_bill_material_data: edit?this.props.record.data.dinamic_bill_material_data:[],
            finalCost: edit?this.props.record.data.price_unit:0
        }
        this.dialog.add(DinamicConfiguratorDialog, {
            // product_template_id: this.props.record.data.product_template_id[0],
            product_id: this.props.record.data.product_id[0],
            ...dinamicData,
            save: async (vals)=>{
                await this.props.record.update({
                    price_unit: vals.finalCost,
                    dinamic_bill_material_data: vals.dinamic_bill_material_data,
                })
            },
            discard: () => {
                saleOrder.order_line.delete(this.props.record);
            },
        });
    },
});
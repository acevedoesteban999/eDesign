/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { SaleOrderLineProductField } from "@sale/js/sale_product_field";

patch(SaleOrderLineProductField.prototype, {
    setup(){
        super.setup()
        this.from_productTemplateUpdate = false
    },
    get isConfigurableTemplate() {
        return this.props.record.data.is_configurable_product || this.props.record.data.is_designable_product;
    },
    async _onProductTemplateUpdate(){
        if(this.props.record.data.is_designable_product)
            this.from_productTemplateUpdate = true
        super._onProductTemplateUpdate()
    },
    async _onProductUpdate() {
        if(this.props.record.data.is_designable_product && this.from_productTemplateUpdate && !this.props.record.fromOnConfirm)
            this._openProductConfigurator()
        

        this.props.record.fromOnConfirm = false;
        this.from_productTemplateUpdate = false;

        super._onProductUpdate()
    },
    _getAdditionalDialogProps() {
        return {
            ...super._getAdditionalDialogProps(),
            record: this.props.record,
        };
    }
});
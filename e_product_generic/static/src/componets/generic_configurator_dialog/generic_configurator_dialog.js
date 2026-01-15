import { _t } from '@web/core/l10n/translation';
import { Dialog } from '@web/core/dialog/dialog';
import { useService } from '@web/core/utils/hooks';
import { Component, onWillStart, useState } from '@odoo/owl';
import { EFloat } from "../e_float/e_float";
import { EMonetary } from "../e_monetary/e_monetary";

export class GenericConfiguratorDialog extends Component {
    static template = 'e_product_generic.GenericConfiguratorDialog';
    static components = { Dialog, EFloat, EMonetary };
    static props = {
        edit: { type: Boolean },
        product_template_id: { type: Number },
        product_template_name: { type: String },
        currencySymbol: { type: String, optional: true, default: "$" },
        currencyPosition: { type: String, optional: true, default: "before" },
        save: { type: Function },
        discard: { type: Function },
        close: Function,
    };

    setup() {
        this.dialog = useService('dialog');
        this.env.dialogData.dismiss = () => this.cancel();
        this.orm = useService('orm');
        this.state = useState({
            generic_bill_material_ids: [],
            finalCost: 0,
            finalCostEdited: false,
            invalidConfirm: false,
        });

        onWillStart(async () => {
            this.state.generic_bill_material_ids = await this.orm.call(
                'product.template',
                'get_generic_bill_material_ids',
                [this.props.product_template_id],
            );

            this.state.generic_bill_material_ids.forEach((gbm) => {
                gbm.qty = 0;
                gbm.invalid = false;
                gbm.final_cost = 0;
                gbm.standard_price = gbm.standard_price || 0;
            });
        });
    }

    onchangeQty(value, generic_product) {
        generic_product.qty = value;
        this._computeFinalCost(generic_product);
        this._computeTotals();
    }

    onchangeInvalid(invalid,generic_product){
        generic_product.invalid = invalid
        this._computeInvalidConfirm()
    }

    onchangePrice(value, generic_product) {
        generic_product.standard_price = value;
        this._computeFinalCost(generic_product);
        this._computeTotals();
    }

    onchangeFinalCost(value, generic_product) {
        generic_product.final_cost = value;
        this._computeTotals();
    }

    _computeFinalCost(generic_product) {
        generic_product.final_cost = generic_product.qty * generic_product.standard_price;
    }

    _computeTotals() {
        const total = this.state.generic_bill_material_ids.reduce((sum, product) => {
            return sum + (product.final_cost || 0);
        }, 0);
        
        if (!this.state.finalCostEdited) {
            this.state.finalCost = total;
        }
    }

    _computeInvalidConfirm() {
        this.state.invalidConfirm = this.state.generic_bill_material_ids.some(gbm => gbm.invalid === true);
    }

    updateFinalCost(value) {
        this.state.finalCost = value;
        this.state.finalCostEdited = true;
    }

    get totalCost() {
        return this.state.generic_bill_material_ids.reduce((sum, product) => {
            return sum + (product.final_cost || 0);
        }, 0);
    }

    async confirm() {
        this.props.save({
            products: this.state.generic_bill_material_ids,
            totalCost: this.totalCost,
            finalCost: this.state.finalCost,
        });
        this.props.close();
    }

    cancel() {
        this.props.close();
    }
}
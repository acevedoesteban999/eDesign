import { _t } from "@web/core/l10n/translation";
import { Component } from "@odoo/owl";
import { EFloat } from "../e_float/e_float";

export class EMonetary extends Component {
    static template = "e_product_generic.EMonetary";
    static components = { EFloat };
    
    static props = {
        value: { type: Number, optional: true },
        update: { type: Function , optional: true},
        invalid:  { type: Function , optional: true},
        digits: { type: Array, optional: true },
        readonly: { type: Boolean, optional: true },
        symbol: { type: String, optional: true, default: "$" },
        class : { type : String , optional: true},
        min: { type: Number, optional: true },
        currencyPosition: { type: String, optional: true, default: "after" }, // "before" o "after"
    };
}
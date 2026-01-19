import { _t } from "@web/core/l10n/translation";
import { formatMonetary } from "@web/views/fields/formatters";
import { EFloat } from "../e_float/e_float";

export class EMonetary extends EFloat {
    static props = {
        ...EFloat.props,
        currencySymbol: { type: String, optional: true },
        currencyPosition: { type: String, optional: true },
    };

    formatMonetaryValue(value) {
        if (value === false || value === null || value === undefined) return "";
        if (!this.props.currencySymbol || !this.props.currencyPosition) return value
        return this.props.currencyPosition === "before"
            ? `${this.props.currencySymbol} ${value}`
            : `${value} ${this.props.currencySymbol}`;
    }

    get displayValue(){
        return this.state.hasFocus?super.displayValue:this.formatMonetaryValue(super.displayValue)
    }
}
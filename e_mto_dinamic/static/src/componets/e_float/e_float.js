import { _t } from "@web/core/l10n/translation";
import { formatFloat } from "@web/views/fields/formatters";
import { parseFloat } from "@web/views/fields/parsers";
import { Component, useState } from "@odoo/owl";

export class EFloat extends Component {
    static template = "e_mto_dinamic.EFloat";
    static props = {
        readonly: { type: Boolean, optional: true },
        value: { type: Number, optional: true },
        digits: { type: Array, optional: true },
        update: { type: Function, optional: true },
        invalid: { type: Function, optional: true },
        class: { type: String, optional: true },
        min: { type: Number, optional: true },
    };
    
    setup() {
        this.state = useState({
            hasFocus: false,
            isInvalid: false,
        });
        this.inputValue = String(this.props.value)
    }

    get displayValue(){
        return this.formatValue(this.props.value)
    }

    formatValue(value) {
        if (value === false || value === null || value === undefined) {
            return "";
        }
        return formatFloat(value, { digits: this.props.digits });
    }

    onInput(ev) {
        this.inputValue = ev.target.value;
    }

    onFocusIn(ev) {
        ev.target.select()
    }
    
    onFocusOut() {
        this._saveValue();
    }

    _saveValue() {
        try {
            let parsedValue = parseFloat(this.inputValue);

            if (this.props.min !== undefined && parsedValue < this.props.min) {
                this.state.isInvalid = true;
            } else {
                this.state.isInvalid = false;
                if (this.props.update) this.props.update(parsedValue);
            }
        } catch (error) {
            this.state.isInvalid = true;
        } finally {
            if (this.props.invalid) this.props.invalid(this.state.isInvalid);
        }
    }
}
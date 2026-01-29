/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { Component, onWillStart, useState } from "@odoo/owl";

export class PotTranslationDialog extends Component {
    static template = "ir_module_e_translate.PotTranslationDialog";
    static components = { Dialog };
    
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            datas: {},
            availableLangs: [],
        });
        this.lang_installed = [];
        
        onWillStart(async() => {
            await this.loadData();
        });
    }

    async loadData() {
        const response = await this.orm.call(
            "ir.module.e_translate",
            "get_pot_translation_data",
            [this.props.action.context.e_translate_id],
        );
        this.state.datas = response.datas || {};
        this.lang_installed = response.lang_installed || [];
        this._updateAvailableLangs();
    }

    _updateAvailableLangs() {
        const currentLangs = Object.keys(this.state.datas);
        this.state.availableLangs = this.lang_installed.filter(
            (code) => !currentLangs.includes(code)
        );
    }

    addLang(ev) {
        const select = ev.target;
        const langCode = select.value;
        if (!langCode) return;

        const firstLang = Object.keys(this.state.datas)[0];
        if (!firstLang) return;

        const keys = Object.keys(this.state.datas[firstLang].data);
        const emptyData = {};
        keys.forEach(key => {
            emptyData[key] = '';
        });

        this.state.datas = {
            ...this.state.datas,
            [langCode]: {
                readonly: false,
                data: emptyData,
                from_ui: true,
            }
        };

        this._updateAvailableLangs();
        select.value = "";
    }

    removeLang(langCode) {
        if (!this.state.datas[langCode] || this.state.datas[langCode].readonly) {
            return;
        }

        const newDatas = {...this.state.datas};
        delete newDatas[langCode];
        
        this.state.datas = newDatas;
        this._updateAvailableLangs();
    }
}

registry.category("actions").add("pot_translation_dialog", PotTranslationDialog);
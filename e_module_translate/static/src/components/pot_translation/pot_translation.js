/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { Component, onWillStart, useState } from "@odoo/owl";

export class PotTranslationDialog extends Component {
    static template = "ir_module_e_translate.PotTranslationDialog";
    static props = ["*"];
    
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.state = useState({
            datas: {},
            availableLangs: [],
            translating: false,
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

    async translateLang(langCode) {
        if (!this.state.datas[langCode] || this.state.datas[langCode].readonly) {
            return;
        }
        
        try {
            const firstLang = Object.values(this.state.datas)[0];
            if (!firstLang) return;
            
            
            const missingKeys = Object.keys(firstLang.data).filter(key => {
                const val = this.state.datas[langCode].data[key];
                return val == null || val === '';
            });
            
            if (missingKeys.length === 0) {
                this.notification.add("No empty values to translate", {type: 'info'});
                return;
            }
            this.state.translating = langCode; 
            
            const textsToTranslate = {};
            missingKeys.forEach(key => {
                textsToTranslate[key] = firstLang.data[key];
            });
            
            const translations = await this.orm.call(
                "ir.module.e_translate",
                "translate_po_values",
                [langCode, textsToTranslate]
            );
    
            if (translations && Object.keys(translations).length > 0) {
                const updatedData = {...this.state.datas[langCode].data};
                
                Object.entries(translations).forEach(([key, value]) => updatedData[key] = value);
    
                this.state.datas = {
                    ...this.state.datas,
                    [langCode]: {
                        ...this.state.datas[langCode],
                        data: updatedData
                    }
                };
    
                this.notification.add(
                    `Translated ${Object.keys(translations).length} strings to ${langCode}`, 
                    {type: 'success'}
                );
            } else {
                this.notification.add("Translation returned empty", {type: 'warning'});
            }
        } catch (error) {
            this.notification.add("Translation error. Please try again.", {type: 'danger'});
            console.error(error);
        } finally {
            this.state.translating = false;
        }
    }

    closeDialog() {
        this.data.close();
    }

    async savePo() {
        this.notification.add("Save functionality coming soon...", {type: 'info'});
        this.closeDialog();
    }
}

registry.category("actions").add("pot_translation_dialog", PotTranslationDialog);
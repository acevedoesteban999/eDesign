/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { Component, onWillStart, useState } from "@odoo/owl";

export class PotTranslationDialog extends Component {
    static template = "ir_module_e_translate.PotTranslationDialog";
    static components = { Dialog };
    static props = ["*"];
    
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.state = useState({
            datas: {},
            availableLangs: [],
            translating: false,
            overwriteExisting: false,
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
            
            let keysToCheck;
            if (this.state.overwriteExisting) {
                keysToCheck = Object.keys(firstLang.data);
            } else {
                keysToCheck = Object.keys(firstLang.data).filter(key => {
                    const val = this.state.datas[langCode].data[key];
                    return val == null || val === '';
                });
            }
            
            if (keysToCheck.length === 0) {
                this.notification.add("No values to translate", {type: 'info'});
                return;
            }
            this.state.translating = langCode; 
            
            const textsToTranslate = {};
            keysToCheck.forEach(key => {
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
                    `Translated ${Object.keys(translations).length} strings to '${langCode}'`, 
                    {type: 'success'}
                );
            
            } else{
                this.notification.add("Translation returned empty", {type: 'warning'});
            }
        } catch (error) {
            this.notification.add("Translation error. Please try again.", {type: 'danger'});
            console.error(error);
        } finally {
            if (this.state.translating === langCode) {
                this.state.translating = false;
            }
        }
    }

    async translateAll() {
        const targetLangs = Object.keys(this.state.datas).filter(
            langCode => !this.state.datas[langCode].readonly
        );
        
        if (targetLangs.length === 0) {
            this.notification.add("No languages to translate", {type: 'warning'});
            return;
        }
        
        this.state.translating = 'all'; 
        
        try {
            for (const langCode of targetLangs)
                await this.translateLang(langCode);
            
            this.notification.add(`Translated all languages`, {type: 'success'});
        } finally {
            this.state.translating = false;
        }
    }

    closeAction() {
        this.action.doAction({type: 'ir.actions.act_window_close'});
    }

    async savePo() {
        try {
            const firstLang = Object.keys(this.state.datas)[0];
            if (!firstLang) {
                throw new Error("No data to save");
            }
            
            this.state.translating = 'saving'; 
            
            const result = await this.orm.call(
                "ir.module.e_translate",
                "save_translate_data", 
                [this.props.action.context.e_translate_id, this.state.datas]
            );
            
            if (!result || !result.success) {
                throw new Error(result?.message || "Save failed");
            }
            
            this.notification.add(result.message || "Translations saved successfully", {
                type: 'success'
            });
            
            this.closeAction();
            
        } catch (error) {
            this.notification.add(error.message || "Error saving translations", {
                type: 'danger'
            });
            console.error(error);
        } finally {
            this.state.translating = false;
        }
    }
}

registry.category("actions").add("pot_translation_dialog", PotTranslationDialog);
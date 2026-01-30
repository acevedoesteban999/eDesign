# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import os
from ..utils.utils import compare_pot_files, get_pot_from_export, get_po_from_file
from ..utils.translate import translate_values , generate_po_content

class IrModuleTranslate(models.Model):
    _name = 'ir.module.e_translate'
    _inherit = "ir.module.e_base"
    _description = 'Translation Manager for Modules'

    has_pot_translations = fields.Boolean("Pot File", compute="_compute_translations")
    po_languages = fields.Json("PO Languages", compute="_compute_translations")
    status = fields.Selection([
        ('up_to_date', "Up to Date"),
        ('out_of_date', "Out of Date"),
        ('error', 'Error'),
    ], readonly=True, default='up_to_date')


    @api.depends('module_name')
    def _compute_translations(self):
        for rec in self:
            rec.has_pot_translations = False
            po_languages = []
            
            if rec.module_exist:
                i18n_path = os.path.join(rec.local_path, 'i18n')
                if os.path.exists(i18n_path):
                    pot_file = os.path.join(i18n_path, f'{rec.module_name}.pot')
                    rec.has_pot_translations = os.path.exists(pot_file)
                    
                    for entry in os.scandir(i18n_path):
                        if entry.name.endswith('.po'):
                            lang_code = entry.name[:-3]
                            po_languages.append({'name': lang_code})
                            
            rec.po_languages = po_languages
            rec.last_check = fields.Datetime.now()

    def action_compute_translations(self):
        self._compute_translations()

    def action_recompute_pot(self):
        self.ensure_one()
        try:
            self._compute_translations()
            result = compare_pot_files(self.local_path, self.module_name, self._cr)
            
            if result:
                common_keys, missing_in_file, extra_in_file = result
                is_outdated = bool(missing_in_file or extra_in_file)
                
                self.status = 'out_of_date' if is_outdated else 'up_to_date'
                self.error_msg = (
                    _("Missing: %s ; Extra: %s") % (len(missing_in_file), len(extra_in_file))
                    if is_outdated else False
                )
                self.last_check = fields.Datetime.now()
            else:
                self.status = 'error'
                self.error_msg = _("No Pot files Generated")
                
        except Exception as e:
            self.status = 'error'
            self.error_msg = str(e)

    @api.model
    def get_pot_translation_data(self, e_translate_id):
        rec = self.browse(e_translate_id)
        if not rec.module_exist:
            return {}
            
        exported_pot = get_pot_from_export(rec.module_name, rec._cr)
        exported_keys = {entry.msgid: entry.msgid for entry in exported_pot if entry.msgid}
        
        installed_langs = self.env['res.lang'].get_installed()
        existing_langs = {l['name'] for l in rec.po_languages}
        
        datas = {
            'POT': {
                'readonly': True,
                'data': exported_keys,
            }
        }
        
       
        for lang in existing_langs:
            try:
                po = get_po_from_file(rec.local_path, lang)
                if po:
                    datas[lang] = {
                        'readonly': False,
                        'data': {entry.msgid: entry.msgstr for entry in po if entry.msgid}
                    }
            except Exception as e:
                pass
                # _logger.warning(f"Error loading PO for {lang}: {e}")
        
        return {
            'datas': datas,
            'lang_installed': [
                lang[0] for lang in installed_langs 
                if lang[0] not in existing_langs and lang[0] != 'en_US'
            ]
        }

    @api.model
    def translate_po_values(self, lang_code, texts_to_translate) -> dict:
        if not (lang_code and texts_to_translate and isinstance(texts_to_translate, dict)):
            return {}
        
        keys = list(texts_to_translate.keys())
        values = list(texts_to_translate.values())
        try:
           
            translations = translate_values(
                values,
                lang_code,
                40,  
                0.5,
            )
            if not translations:
                return {}
            
            result = {}
            for key, translated in zip(keys, translations):
                result[key] = translated
                
            return result
            
        except Exception as e:
            return {}
    
    def generate_po_file(self, lang_code: str, pot_data: dict, all_translations: dict): 
        pot_metadata = {}
        i18n_path = os.path.join(self.local_path, 'i18n')
        pot_path = os.path.join(i18n_path, f'{self.module_name}.pot')
        
        if os.path.exists(pot_path):
            try:
                import polib
                pot_file = polib.pofile(pot_path)
                pot_metadata = pot_file.metadata
            except Exception:
                pass
        
        po_content = generate_po_content(
            pot_data=pot_data,
            translations_dict=all_translations,
            lang_code=lang_code,
            pot_metadata=pot_metadata
        )
        
        return po_content
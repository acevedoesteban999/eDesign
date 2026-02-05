# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import os
from ..utils.utils import compare_pot_files, get_pot_from_export , get_pots_from_export , get_po_from_file , save_pot_file , save_po_file
from ..utils.translate import translate_values 
import polib
from datetime import datetime
import copy

_POT_DICT_KEY = 'POT'

class IrModuleTranslate(models.Model):
    _name = 'ir.module.e_translate'
    _inherit = "ir.module.e_base"
    _description = 'Translation Manager for Modules'

    po_languages = fields.Json("PO Languages", compute="_compute_state",store=True)
    state = fields.Selection(selection_add=[
        ('synced', "Synced"),
        ('mismatch', "Mismatch"),
        ('missing', "Missing"),
    ], string="Translate State",store=True)

    def _recompute_translations(self,recompute_state = False , pot_file_cached = False):
        po_languages = []
            
        if self.module_state != 'installed':
            self.state = False
            return
            
        try:
            i18n_path = os.path.join(self.local_path, 'i18n')
            os.makedirs(i18n_path, exist_ok=True)
            
            pot_file = os.path.join(i18n_path, f'{self.module_name}.pot')
            has_pot_translations = os.path.exists(pot_file)
            
            if has_pot_translations:
                if recompute_state:
                    result = compare_pot_files(self.local_path, self.module_name, self._cr , pot_file_cached)
                    if result:
                        common_keys, missing_in_file, extra_in_file = result
                        if missing_in_file or extra_in_file:
                            self.state = 'mismatch'
                            self.error_msg = (_("Missing: %s ; Extra: %s") % (len(missing_in_file), len(extra_in_file)))
                        else:
                            self.state = 'synced'
                    else:
                        self.state = False
            else:
                self.state = 'missing'
                
            for entry in os.scandir(i18n_path):
                if entry.name.endswith('.po'):
                    lang_code = entry.name[:-3]
                    po_languages.append({'name': lang_code})
                    
        except Exception:
            self.state = 'error'
                        
        self.po_languages = po_languages
        self.last_check = fields.Datetime.now()
    
    def _compute_state(self):
        for rec in self:
            super(IrModuleTranslate,rec)._compute_state()
            rec.po_languages = []
            rec._recompute_translations()

    def action_recompute_data(self ,recompute_state = False ,cach_pot = False):
        _recompute_state = recompute_state or self.env.context.get('recompute_state')
        if cach_pot:
            records = self.filtered_domain([('module_state','=','installed')])
            pots = get_pots_from_export(records.mapped('module_name'),self._cr)
            for rec,pot_file in zip(records,pots):
                rec._recompute_translations(_recompute_state,pot_file)
        else:
            for rec in self:
                rec._recompute_translations(_recompute_state)
        

    @api.model
    def get_pot_translation_data(self, e_translate_id, pot_file_cached = False):
        rec = self.browse(e_translate_id)
        if rec.module_state != 'installed':
            return {}
        
        if not pot_file_cached:
            exported_pot = get_pot_from_export(rec.module_name, rec._cr)
        else:
            exported_pot = pot_file_cached
            
        header_comment = exported_pot.header
        
        pot_metadata = exported_pot.metadata
        pot_entries = {}
        simple_data = {} 
        
        for entry in exported_pot:
            if not entry.msgid:
                continue
            
            pot_entries[entry.msgid] = {
                'msgid': entry.msgid,
                'msgctxt': entry.msgctxt or '',
                'comment': entry.comment or '',
                'tcomment': entry.tcomment or '',
                'occurrences': entry.occurrences or [],
                'flags': entry.flags or [],
            }
            simple_data[entry.msgid] = entry.msgid
        
        
        installed_langs = [code for code in self.env['res.lang']._get_active_by('iso_code').keys() if code != 'en']
        existing_langs = {l['name'] for l in rec.po_languages if l} if rec.po_languages else {}
        
        datas = {
            _POT_DICT_KEY: {
                'readonly': True,
                'metadata': pot_metadata,
                'header_comment': header_comment,
                'entries': pot_entries,     
                'data': simple_data    
            }
        }
        
        
        for lang in existing_langs:
            try:
                po = get_po_from_file(rec.local_path, lang)
                if po:
                    po_data = {}
                    for entry in po:
                        if entry.msgid:
                            po_data[entry.msgid] = entry.msgstr
                    datas[lang] = {
                        'readonly': False,
                        'data': po_data
                    }
            except Exception:
                pass
        
        return {
            'datas': datas,
            'lang_installed': installed_langs
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
    
    @api.model
    def save_translate_data(self, e_translate_id, save_data):
        rec = self.browse(e_translate_id)
        if rec.module_state != 'installed' or not rec.local_path:
            raise UserError(_("Module error:  Not (Installed or Found)"))
        
        i18n_path = os.path.join(rec.local_path, 'i18n')
        os.makedirs(i18n_path, exist_ok=True)
        
        pot_info = save_data.get('POT', {})
        pot_metadata = pot_info.get('metadata', {})
        pot_entries = pot_info.get('entries', {})
        header_comment = pot_info.get('header_comment', '')
        
        if not pot_entries:
            raise UserError(_("No POT data found"))
        
        pot_file = polib.POFile()
        pot_file.metadata = pot_metadata
        pot_file.header = header_comment
        
        
        for msgid, entry_data in pot_entries.items():
            if not msgid: 
                continue
            entry = polib.POEntry(
                msgid=entry_data['msgid'],
                msgstr='',
                msgctxt=entry_data.get('msgctxt') or None,
                comment=entry_data.get('comment') or '',
                tcomment=entry_data.get('tcomment') or '',
                occurrences=entry_data.get('occurrences', []),
                flags=entry_data.get('flags', [])
            )
            pot_file.append(entry)
        
        pot_path = os.path.join(i18n_path, f'{rec.module_name}.pot')
        pot_file.save(pot_path)
        
        
        saved_pos = []
        
        for lang_code, lang_info in save_data.items():
            if lang_code == 'POT':
                continue
                
            translations = lang_info.get('data', {})
            
            po_file = copy.deepcopy(pot_file)
            
            po_file.metadata.update({
                'Language': lang_code,
                'PO-Revision-Date': datetime.now().strftime('%Y-%m-%d %H:%M%z'),
                'Last-Translator': 'e_module_translate <acevedoesteban999@gmail.com>',
                'Language-Team': f'e_module_translate <acevedoesteban999@gmail.com>',
                'X-Generator': 'e_module_translate',
            })
                
            if 'Plural-Forms' not in po_file.metadata:
                po_file.metadata['Plural-Forms'] = 'nplurals=2; plural=(n != 1);'
            
            entries_with_translation = []
            for entry in po_file:
                msgstr = translations.get(entry.msgid, '')
                if msgstr and str(msgstr).strip():
                    entry.msgstr = msgstr
                    entries_with_translation.append(entry)
            
            po_file[:] = entries_with_translation
            
            po_path = os.path.join(i18n_path, f'{lang_code}.po')
            
            if entries_with_translation:
                po_file.save(po_path)
                saved_pos.append(lang_code)
            elif os.path.exists(po_path):
                os.remove(po_path)
        
        rec._recompute_translations(True)
        rec.error_msg = False
        rec.last_check = fields.Datetime.now()
        
        return {
            'success': True,
            'message': _(f"Saved POT and {len(saved_pos)} translation files"),
            'pot_file': f'{rec.module_name}.pot',
            'po_files': saved_pos
        }
        
    def action_open_autotranslate_wizard(self):
        return {
            'name': _('Autotranslate'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'ir.module.e_translate.autotranslate.wizard',
            'domain': [],
            'context': {
                'e_translation_ids': self.ids
            }
        }
        
    def action_open_addon_modules_wizard(self):
        return {
            'name': _('Import Modules Translate'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'e_module_base.addon_modules_wizard',
            'views': [(self.env.ref('e_module_translate.view_addon_modules_etranslate_wizard_form').id,'form')],
            'domain': [],
            'context': {}
        }
        
        
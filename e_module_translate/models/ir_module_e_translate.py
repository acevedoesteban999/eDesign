# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
import os
from ..utils.utils import compare_pot_files  , get_pot_from_export , get_po_from_file
NEW_LANG_KEY = '__new__'

class Ir_moduleTranslate(models.Model):
    _name = 'ir.module.e_translate'
    _inherit = "ir.module.e_base"
    _description = 'irModuleTranslate'

    
    has_pot_translations = fields.Boolean("Pot File",compute="_compute_translations")
    po_languages = fields.Json("PO Languages",compute="_compute_translations")
    
    status = fields.Selection([
        ('up_to_date',"Up to Date"),
        ('out_of_date',"Out of Date"),
        ('error','Error'),
    ],readonly=True)
    
    
    
    @api.depends('module_name')
    def _compute_translations(self):
        for rec in self:
            rec.has_pot_translations = False
            po_languages = []
            if rec.module_exist:
                i18n_path = os.path.join(rec.local_path,'i18n')
                if os.path.exists(i18n_path):
                    for entry in os.scandir(i18n_path):
                        if entry.name == f'{rec.module_name}.pot':
                            rec.has_pot_translations = True
                        elif entry.name.endswith('.po'):
                            lang_code = entry.name[:-3]
                            po_languages.append({
                                'name': lang_code,
                            })
            rec.po_languages = po_languages
            rec.last_check = fields.Datetime.now()
              
    def action_compute_translations(self):
        self._compute_translations()
        
        
    def action_recompute_pot(self):
        self.ensure_one()
        try:
            self._compute_translations()
            result = compare_pot_files(self.local_path,self.module_name,self._cr)
            if result:
                common_keys, missing_in_file, extra_in_file = result
                self.status = 'out_of_date' if bool(missing_in_file and extra_in_file) else 'up_to_date'
                if self.status == 'out_of_date':
                    self.error_msg = _("Missing: %s ; Extra: %s") % (len(missing_in_file) , len(extra_in_file))
                else:
                    self.error_msg = False
                self.last_check = fields.Datetime.now()
            else:
                self.status = 'error'
                
                self.error_msg = _("No Pot files Generated")
        except Exception as e:
            self.status = 'error'
            self.error_msg = str(e)
            
    @api.model
    def get_pot_translation_data(self,e_translate_id):
        rec = self.env['ir.module.e_translate'].browse(e_translate_id)
        if not rec.module_exist:
            return {}
        exported_pot = get_pot_from_export(rec.module_name,rec._cr)
        exported_keys = {entry.msgid:entry.msgid for entry in exported_pot if entry.msgid}
        langs = [l['name'] for l in rec.po_languages if l.get('name')]
        datas = {
            'POT': {
                'readonly': True,
                'data':exported_keys,
            }
        }
        
        for lang in langs:
            try:
                po = get_po_from_file(rec.local_path,lang)
                po_data = { entry.msgid:entry.msgstr for entry in po if entry.msgid}
                if po:
                    datas.update({
                        lang: {
                            'readonly': False,
                            'data':po_data,                        
                        }
                    })
            except:
                pass
        return {
            'datas': datas,
            'lang_installed': [lang[0] for lang in self.env['res.lang'].get_installed() if lang[0] not in langs]
        }
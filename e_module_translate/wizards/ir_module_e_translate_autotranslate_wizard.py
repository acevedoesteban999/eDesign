
from odoo import models, fields, _
from ..models.ir_module_e_translate import _POT_DICT_KEY 
from ..utils.utils import get_pots_from_export
class ModelName(models.TransientModel):
    _name = 'ir.module.e_translate.autotranslate.wizard'
    _description = 'eModuleAutotranslate'
    
    languages = fields.Many2many('res.lang','res_autotrans_lang',domain="[('iso_code','!=','en')]",string="Languages",required=True)
    
    
    def action_autotranslate(self):
        self.ensure_one()
        e_translation_model = self.env['ir.module.e_translate']
        e_translation_ids = self.env.context.get('e_translation_ids', [])
        
        if not e_translation_ids:
            return {'type': 'ir.actions.act_window_close'}
        
        e_translations = e_translation_model.browse(e_translation_ids).filtered_domain([('module_state','=','installed')])
        modules_name = e_translations.mapped('module_name')
        
        pots = get_pots_from_export(modules_name,self._cr)
        
        for e_translation,pot_file in zip(e_translations,pots):
            try:    
                if e_translation.module_state != 'installed':
                    continue
                
                e_translation._recompute_translations(True,pot_file)
                if e_translation.state not in ['outdated','missing']:
                    continue
                
                result = e_translation.get_pot_translation_data(e_translation.id,pot_file)
                if not result or 'datas' not in result:
                    continue
                
                datas = result['datas']
                pot_info = datas.get(_POT_DICT_KEY, {})
                pot_entries = pot_info.get('entries', {})
                
                if not pot_entries:
                    continue
                
                save_payload = {
                    _POT_DICT_KEY: pot_info
                }
                
                for lang in self.languages:
                    
                    trans_code = lang.iso_code or lang.code
                    
                    existing_data = datas.get(trans_code, {}).get('data', {})
                    
                    
                    to_translate = {
                        entry['msgid']: entry['msgid'] 
                        for entry in pot_entries.values() 
                        if not existing_data.get(entry['msgid'])
                    }
                    
                    if to_translate:
                        
                        translations = e_translation_model.translate_po_values(
                            trans_code, 
                            to_translate
                        )
                        existing_data.update(translations)
                    
                    save_payload[trans_code] = {
                        'readonly': False,
                        'data': existing_data
                    }
            
                e_translation.save_translate_data(e_translation.id, save_payload)
            except Exception as e:
                pass
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _("Translations Completed"),
                'type': 'success',
                'sticky': False,
                'next':{
                    'type': 'ir.actions.act_window_close'
                }
                    
            }
        }
        

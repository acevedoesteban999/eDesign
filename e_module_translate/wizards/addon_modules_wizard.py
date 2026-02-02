# -*- coding: utf-8 -*-

import os
from odoo import models, _

class AddonModules(models.TransientModel):
    _inherit = 'e_module_base.addon_modules_wizard'
    
    def _compute_modules(self):
        if self.env.context.get('active_model') == 'ir.module.e_translate':
            for rec in self:
                if not rec.addon_path or not os.path.exists(rec.addon_path):
                    rec.modules = []
                    continue
                if rec.addon_modules:
                    addon_modules = [module.get('name') for module in rec.addon_modules]
                    modules_translation = self.env['ir.module.e_translate'].search([]).mapped('module_name')
                    if modules_translation:
                        rec.modules = [{"name": mod} for mod in addon_modules if mod not in modules_translation]
                        continue
                rec.modules = []
        else:
            super()._compute_modules()
       
    def load_translate_modules(self):
        if self.env.context.get('active_model') == 'ir.module.e_translate':
            for module in self.modules:
                module_name = module.get('name')
                if not self.env['ir.module.e_translate'].search([('module_name','=',module_name)]):
                    self.env['ir.module.e_translate'].create({
                        'module_id': self.env['ir.module.module'].search([('name','=',module_name)]).id
                    })
        
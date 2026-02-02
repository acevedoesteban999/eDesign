# -*- coding: utf-8 -*-

import os
from odoo import models, fields, api, _


class AddonModules(models.TransientModel):
    _inherit = 'e_module_base.addon_modules_wizard'
    
    
    def _compute_modules(self):
        if self.env.context.get('res_model') == 'ir.module.e_translate':
            pass
        super()._compute_modules()
       
    def load_modules(self):
        pass
        
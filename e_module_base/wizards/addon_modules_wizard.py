# -*- coding: utf-8 -*-

import os
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

from ..utils.util import scan_addon_path , _os_path_dir



class AddonModules(models.TransientModel):
    _name = 'e_module_base.addon_modules_wizard'
    _description = "Get Modules by Addon Path"

    addon_path = fields.Char("Addon Path", default=lambda self: _os_path_dir(os.path.abspath(__file__),3))
    modules = fields.Json("Modules Found", compute="_compute_modules", store=False)
    modules_not_installed = fields.Json("Modules Not Installed", compute="_compute_modules", store=False)
    
    @api.depends('addon_path')
    def _compute_modules(self):
        for record in self:
            if not record.addon_path or not os.path.exists(record.addon_path):
                record.modules = []
                record.modules_not_installed = []
                continue
            
            found_modules = scan_addon_path(record.addon_path)
            
            installed_modules = self.env['ir.module.module'].sudo().search([
                ('state', '=', 'installed')
            ]).mapped('name')
            
            not_installed = [mod for mod in found_modules if mod['name'] not in installed_modules]
            
            record.modules = [{"name": mod['name']} for mod in found_modules]
            record.modules_not_installed = [{"name": mod['name']} for mod in not_installed]
            
    def action_scan(self):
        self.ensure_one()
        self._compute_modules()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
        
    def loadModules(self):
        return {'type': 'ir.actions.act_window_close'}
        
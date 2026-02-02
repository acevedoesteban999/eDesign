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
    addon_modules = fields.Json("Modules Found", compute="_compute_addons_modules",store=True)
    modules = fields.Json("Modules", compute="_compute_modules", readonly=False,store=True)
    
    
    @api.depends('addon_path')
    def _compute_addons_modules(self):
        for rec in self:
            if not rec.addon_path or not os.path.exists(rec.addon_path):
                rec.addon_modules = []
                continue
            
            found_modules = scan_addon_path(rec.addon_path)
            if found_modules:
                rec.addon_modules = [{"name": mod['name']} for mod in found_modules]
            else:
                rec.addon_modules = []
    
    @api.depends('addon_path')
    def _compute_modules(self):
        for rec in self:
            if not rec.addon_path or not os.path.exists(rec.addon_path):
                rec.modules = []
                continue
            
            installed_modules = self.env['ir.module.module'].sudo().search([
                ('state', '=', 'installed')
            ]).mapped('name')
            if rec.addon_modules and installed_modules:
                not_installed = [mod for mod in rec.addon_modules if mod['name'] not in installed_modules]
                if not_installed:
                    rec.modules = [{"name": mod['name']} for mod in not_installed]
                    continue
            rec.modules = []
    
            
# -*- coding: utf-8 -*-
# Copyright 2025 
# License LGPL-3

from odoo import models, fields, api, _ , modules
from odoo.modules import get_manifest

class EGithubModuleUpdater(models.AbstractModel):
    _name = 'ir.module.e_update'
    _description = 'Base Module Updater'
    _rec_name = 'module_name'

    module_name = fields.Char("Module Technical Name", required=True)
    local_version = fields.Char("Local Version", compute="_compute_versions")
    installed_version = fields.Char("Installed Version", compute="_compute_versions")
    
    _sql_constraints = [
        ('unique_module', 'unique(module_name)', 'Module must be unique!')
    ]
    
    def _get_github_api_headers(self):
        return {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Odoo-GitHub-Updater'
        }

    def _get_module_local_path(self):
        self.ensure_one()
        return  modules.get_module_path(self.module_name)
    
    def _get_module_local_version(self):
        self.ensure_one()
        return get_manifest(self.module_name).get('version')
    
    @api.depends('module_name')
    def _compute_versions(self):
        for record in self:
            if not record.module_name:
                record.update({
                    'local_version': _("Unknown"),
                    'installed_version': _("Unknown"),
                })
                continue
            
            local_version = record._get_module_local_version()
            installed_version = self.env['ir.module.module'].search([('name','=',self.module_name)]).installed_version
            
            record.update({
                'local_version': local_version or _("Unknown"),
                'installed_version':installed_version or _("Unknown"),
            })

    # ===================================================================
    # ACTIONS
    # ===================================================================

    def action_check_version(self):
        self.ensure_one()
        self._compute_versions()
        
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Version Check'),
                'type': 'info',
                'sticky': False,
            }
        }
        
    def action_update_module(self):
        pass
    
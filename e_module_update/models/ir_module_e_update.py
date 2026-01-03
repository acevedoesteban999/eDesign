# -*- coding: utf-8 -*-
# Copyright 2025 
# License LGPL-3

from odoo import models, fields, api, _ , modules 
from odoo.exceptions import UserError
from odoo.modules import get_manifest
from ..utils.util import make_backup

class EGithubModuleUpdater(models.AbstractModel):
    _name = 'ir.module.e_update'
    _description = 'Base Module Updater'
    _rec_name = 'module_name'

    module_name = fields.Char("Module Technical Name", required=True)
    module_icon = fields.Char(compute="_compute_module_icon")
    module_exist = fields.Boolean("Module Exist",compute="_compute_module_exist")
    local_version = fields.Char("Local Version", compute="_compute_versions",store=True)
    installed_version = fields.Char("Installed Version", compute="_compute_versions",store=True)
    update_state = fields.Selection([
        ('uptodate', "Up to date"),
        ('to_update', "To Update"),
        ('error', "Error"),
    ], compute="_compute_versions", store=True,default=False,)
    update_local = fields.Boolean(compute="_compute_update_local")
    error_msg = fields.Char("Error")
    last_check = fields.Datetime("Last Check")
    backup_ids = fields.One2many('ir.module.e_update.backup','e_update_module_id',"Backups",compute="_compute_backup_ids")
    _sql_constraints = [
        ('unique_module', 'unique(module_name)', 'Module must be unique!')
    ]
    
    @api.onchange('module_name')
    def _compute_module_icon(self):
        for rec in self:
            rec.module_icon = f"/{self.module_name}/static/description/icon.png"
    
    def _compute_backup_ids(self):
        for rec in self:
            rec.backup_ids = False
    
    @api.depends('module_name')
    def _compute_module_exist(self):
        for rec in self:
            rec.module_exist = rec.module_name and  rec.env['ir.module.module'].search_count([('name','=',rec.module_name)]) != 0 or False
    
    @api.depends('local_version','installed_version')
    def _compute_update_local(self):
        for rec in self:
            rec.update_local = self.version_to_tuple(rec.local_version) != self.version_to_tuple(rec.installed_version) 
    
    @staticmethod
    def version_to_tuple(v):
        try:
            parts = str(v).split('.')
            return tuple(int(p) for p in parts if p.isdigit())
        except:
            return False
    
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
            if not record.module_exist:
                record.update({
                    'local_version': _("Unknown"),
                    'installed_version': _("Unknown"),
                    'update_state': 'error' if record.module_name else False,
                    'error_msg': _('Module not found') if record.module_name else False,
                })
                continue
            
            local_version = record._get_module_local_version()
            installed_version = self.env['ir.module.module'].search([('name','=',self.module_name)]).installed_version
            
            record.update({
                'local_version': local_version or _("Unknown"),
                'installed_version':installed_version or _("Unknown"),
            })
            self.compute_update_state(local_version,installed_version)
            
    def compute_update_state(self,new_version, local_version, error_if_not_version = False):
        new_version = self.version_to_tuple(new_version)
        local_version = self.version_to_tuple(local_version)
        if new_version and local_version:
            if new_version > local_version:
                update_state = 'to_update'
                error_msg = False
            elif new_version == local_version:
                update_state = 'uptodate'
                error_msg = _("Versions are identical")
            else:
                update_state = 'error'
                error_msg = _("Version is older than module's version")
        else:
            update_state = False
            error_msg = error_if_not_version or _("Versions not set")
        
        self.write({
            'update_state':update_state,
            'error_msg':error_msg,
            'last_check': fields.Datetime.now(),
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
    
    def action_store_version(self):
        "Generate Backup"
        if self.update_state != 'to_update':
            raise UserError(_("Cannot update: %s") % (self.error or _("Invalid state")))
        
        if not self.local_version:
            raise UserError(_("No local version provided"))
        
        local_path = self._get_module_local_path()
        
        if not local_path:
            raise UserError(_("No local path provided"))
        
        backup_path = make_backup(
            local_path=local_path,
            module_name=self.module_name,
            version=self.local_version
        )
        "The inherit model replace the local module folder"
        return local_path,backup_path
    

    def action_install_local_version(self):
        self.ensure_one()
        
        module = self.env['ir.module.module'].search([('name', '=', self.module_name)], limit=1)
        
        if not module:
            raise exceptions.UserError(_("Module '%s' not found in repository") % self.module_name)
        
        if module.state not in ['installed', 'to upgrade']:
            raise exceptions.UserError(_("Module '%s' is not installed (state: %s)") % (self.module_name, module.state))
        
        try:
            module.button_immediate_upgrade()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Module Update'),
                    'message': _('%s is being updated...') % self.module_name,
                    'type': 'warning',
                    'sticky': False,
                    'next': {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    },
                }
            }
        except Exception as e:
            raise exceptions.UserError(_("Update failed: %s") % str(e))
    
    def action_store_and_install_version(self):
        self.action_store_version()
        self.action_install_local_version()
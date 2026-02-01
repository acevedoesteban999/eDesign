# -*- coding: utf-8 -*-
# Copyright 2025 
# License LGPL-3

from odoo import models, fields, api, _ , modules , Command
from odoo.exceptions import UserError
from ..utils.util import make_backup , get_module_backups
from odoo.modules.module import load_manifest

class EGitModuleUpdater(models.AbstractModel):
    _name = 'ir.module.e_update'
    _inherit = 'ir.module.e_base'
    _description = 'Base Module Updater'
    _rec_name = 'module_name'

    
    local_version = fields.Char("Local Version", compute="_compute_versions",
                                help="Version Cached in Odoo. Need Restart Odoo Server for changes")
    
    repository_version = fields.Char("Repository Version", compute="_compute_versions",
                                     help="Version on Repository(Disk, Folder , OS)")
    
    update_state = fields.Selection([
        ('uptodate', "Up to date"),
        ('to_update', "To Update"),
        ('to_downgrade',"To Downgrade"),
        ('error', "Error"),
    ], compute="_compute_versions",default=False,)
    
    update_local = fields.Boolean(compute="_compute_update_local")
    restart_local = fields.Boolean(compute="_compute_restart_local")
    
    backup_ids = fields.Many2many('ir.module.e_update.backup','rel_backups_e_update',string="Backups",compute="_compute_backup_ids",readonly=False)
    
    all_selected = fields.Boolean(compute="_compute_selecteds")
    has_selected = fields.Boolean(compute="_compute_selecteds")
    
    _sql_constraints = [
        ('unique_module', 'unique(module_name)', 'Module must be unique!')
    ]
    
    # ===================================================================
    # API
    # ===================================================================

    @api.depends('backup_ids.selected')
    def _compute_selecteds(self):
        for rec in self:
            count_selecteds = len(rec.backup_ids.filtered_domain([('selected','=',True)]))
            total_selecteds = len(rec.backup_ids)
            rec.all_selected = total_selecteds == count_selecteds
            rec.has_selected = bool(count_selecteds)
        
    
    @api.depends('module_name','module_exist')
    def _compute_backup_ids(self):
        for rec in self:
            rec.backup_ids = False
            if not rec.id:
                continue
            if rec.module_exist:
                rec.backup_ids = rec.backup_ids.get_backups_Command(self.env,rec.module_name)
                    
    
    @api.depends('local_version','installed_version')
    def _compute_update_local(self):
        for rec in self:
            rec.update_local = self.compare_versions(rec.local_version,rec.installed_version) 
    
    @api.depends('repository_version','local_version')
    def _compute_restart_local(self):
        for rec in self:
            rec.restart_local = self.compare_versions(rec.local_version,rec.repository_version) 
   
    # ===================================================================
    # METHODS
    # ===================================================================

    @staticmethod
    def compare_versions(_v1,_v2):
        v1 = EGitModuleUpdater.version_to_tuple(_v1)
        v2 = EGitModuleUpdater.version_to_tuple(_v2) 
        return bool(v1) and bool(v2) and v1 != v2
        
    @staticmethod
    def version_to_tuple(v):
        try:
            parts = str(v).split('.')
            if len(parts) > 1 or parts[0].isdigit():
                return tuple(int(p) for p in parts) 
        except:
            pass
        return False
        
    @api.depends('module_name')
    def _compute_versions(self, update_state = True):
        for rec in self:
            if rec.module_status != 'ready':
                rec.update({
                    'local_version': _("Unknown"),
                    'installed_version': _("Unknown"),
                    'repository_version': _("Unknown"),
                    'update_state': 'error' if rec.module_name else False,
                    'error_msg': _('Module not found') if rec.module_name else False,
                })
                continue
            
            module = self.env['ir.module.module'].search([('name','=',rec.module_name)])
            repository_version = load_manifest(rec.module_name).get('version',_("Unknown"))
            local_version = module.installed_version
            rec._compute_installed_versions()
            
            rec.update({
                'local_version': local_version or _("Unknown"),
                'repository_version': repository_version or _("Unknown"),
            })
            
            if update_state:
                rec.compute_update_state()
            
    def compute_update_state(self):
        self._compute_update_state(self.repository_version,self.local_version)
        if not self.update_state or self.update_state == 'uptodate':
            self._compute_update_state(self.local_version,self.installed_version)
        
    def _compute_update_state(self,up_version, down_version):
        up_version = self.version_to_tuple(up_version)
        down_version = self.version_to_tuple(down_version)
        if up_version and down_version:
            if up_version > down_version:
                update_state = 'to_update'
                error_msg = False
            elif up_version == down_version:
                update_state = 'uptodate'
                error_msg = False
            else:
                update_state = 'to_downgrade'
                error_msg = _("Version is older than module's version")
        else:
            update_state = False
            error_msg = ""
        
        self.write({
            'update_state':update_state,
            'error_msg':error_msg,
            'last_check': fields.Datetime.now(),
        })
    
    # ===================================================================
    # ACTIONS
    # ===================================================================

    def action_select_all_backups(self):
        self.backup_ids.selected = True
    
    def action_unselect_all_backups(self):
        self.backup_ids.selected = False
    
    def action_remove_selected_backups(self):
        self.backup_ids.filtered_domain([('selected','=',True)]).action_delete_backup()

    def action_check_version(self):
        self.ensure_one()
        self._compute_versions()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Version Checked'),
                'type': 'info',
                'sticky': False,
                'next':{'type': 'ir.actions.act_window_close'}
            }
        }
    
    def action_install_local_version(self):
        self.ensure_one()
        
        module = self.env['ir.module.module'].search([('name', '=', self.module_name)], limit=1)
        
        if not module:
            raise UserError(_("Module '%s' not found in repository") % self.module_name)
        
        if module.state not in ['installed', 'to upgrade']:
            raise UserError(_("Module '%s' is not installed (state: %s)") % (self.module_name, module.state))
        
        try:
            module.button_immediate_upgrade()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Module Update'),
                    'message': _("Success update for '%s' !") % self.module_name,
                    'type': 'success',
                    'sticky': False,
                    'next': {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    },
                }
            }
        except Exception as e:
            raise UserError(_("Update failed: %s") % str(e))
        
    def action_restart_server(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
        }
        
    def action_create_backup(self):
        for rec in self:
            if rec.module_status == 'ready':
                make_backup(
                    rec.local_path,
                    rec.module_name,
                    rec.repository_version
                )
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Backup'),
                    'message': _("Success backup created for '%s' !") % self.module_name,
                    'type': 'success',
                    'sticky': False,
                    'next': {
                        'type': 'ir.actions.act_window_close'
                    },
                }
            }
    
    def action_reload_backups(self):
        self._compute_backup_ids()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Backup'),
                'message': _("Success backup reload for '%s' !") % self.module_name,
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close'
                },
            }
        }
            
            
    # ===================================================================
    # ORM
    # ===================================================================
    
    def create(self, values):
        rec = super().create(values)
        rec._compute_backup_ids()
        return rec
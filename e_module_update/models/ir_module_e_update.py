# -*- coding: utf-8 -*-
# Copyright 2025 
# License LGPL-3

from odoo import models, fields, api, _ , modules , Command
from odoo.exceptions import UserError
from ..utils.util import make_backup , get_module_backups
from odoo.modules.module import load_manifest

class eIrModuleUpdate(models.AbstractModel):
    _name = 'ir.module.e_update'
    _inherit = 'ir.module.e_base'
    _description = 'Base Module Updater'
    _rec_name = 'module_name'

    
    repository_version = fields.Char("Repository Version", compute="_compute_repository_version",
                                     help="Version on Repository(Disk, Folder , OS)")
    
    state = fields.Selection(selection_add=[
        ('updated', "Updated"),
        ('to_update', "To Update"),
        ('to_downgrade',"To Downgrade"),
    ],string="Update State")
    
    update_local = fields.Boolean(compute="_compute_update_local")
    restart_local = fields.Boolean(compute="_compute_restart_local")
    
    backup_ids = fields.Many2many(
        'ir.module.e_update.backup',
        'rel_backups_e_update',
        string="Backups",
        compute="_compute_backup_ids",
        readonly=False
    )
    
    all_selected = fields.Boolean(compute="_compute_selecteds")
    has_selected = fields.Boolean(compute="_compute_selecteds")
    
    _sql_constraints = [
        ('unique_module', 'unique(module_name)', 'Module must be unique!')
    ]
    
    # ===================================================================
    # API
    # ===================================================================

    @api.depends('backup_ids')
    def _compute_selecteds(self):
        for rec in self:
            count_selecteds = len(rec.backup_ids.filtered_domain([('selected','=',True)]))
            total_selecteds = len(rec.backup_ids)
            rec.all_selected = total_selecteds == count_selecteds
            rec.has_selected = bool(count_selecteds)
        
    
    @api.depends('module_id')
    def _compute_backup_ids(self):
        for rec in self:
            rec.backup_ids = False
            if not rec.id:
                continue
            if rec.module_id:
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
        v1 = eIrModuleUpdate.version_to_tuple(_v1)
        v2 = eIrModuleUpdate.version_to_tuple(_v2) 
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
        
    @api.depends('module_id')
    def _compute_repository_version(self):
        for rec in self:
            try:
                rec.repository_version = False
                if rec.module_state != 'installed':
                    continue
                
                rec.repository_version = load_manifest(rec.module_name).get('version')
            except:
                rec.state = 'error'
    
    def _get_versions(self):
        return [self.repository_version,self.local_version,self.installed_version]
    
    def _compute_state(self):
        for rec in self:
            try:
                super(eIrModuleUpdate,rec)._compute_state()
                rec._compute_repository_version()
                
                versions = rec._get_versions()
                rec.state = rec._check_version_recursive(versions)
                if rec.state == 'to_downgrade':
                    rec.error_msg = _("Version is older than module's version")
                rec.last_check = fields.Datetime.now()
            except:
                rec.state = 'error'
    
    def _check_version_recursive(self,versions):
        if len(versions) > 1:
            tuple_version = list(zip(versions, versions[1:]))
            for up,down in tuple_version:
                resp = self._check_versions(up,down)
                if resp in ['to_update','to_downgrade']:
                    return resp
        return 'updated'
    
    def _check_versions(self,up_version, down_version):
        up_version = self.version_to_tuple(up_version)
        down_version = self.version_to_tuple(down_version)
        if up_version and down_version:
            if up_version > down_version:
                return 'to_update'
            elif up_version == down_version:
                return 'updated'
            else:
                return 'to_downgrade'
                
        else:
            return False
            
        self.last_check = fields.Datetime.now()
        
    # ===================================================================
    # ACTIONS
    # ===================================================================

    def action_select_all_backups(self):
        self.backup_ids.selected = True
    
    def action_unselect_all_backups(self):
        self.backup_ids.selected = False
    
    def action_remove_selected_backups(self):
        self.backup_ids.filtered_domain([('selected','=',True)]).action_delete_backup()

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
            if rec.module_state == 'installed':
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
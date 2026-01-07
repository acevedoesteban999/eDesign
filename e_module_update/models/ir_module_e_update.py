# -*- coding: utf-8 -*-
# Copyright 2025 
# License LGPL-3

from odoo import models, fields, api, _ , modules , Command
from odoo.exceptions import UserError
from ..utils.util import make_backup , get_backup_list
from odoo.modules.module import load_manifest

class EGitModuleUpdater(models.AbstractModel):
    _name = 'ir.module.e_update'
    _description = 'Base Module Updater'
    _rec_name = 'module_name'

    module_name = fields.Char("Module Technical Name", required=True)
    module_icon = fields.Char(compute="_compute_module_icon")
    module_exist = fields.Boolean("Module Exist",compute="_compute_module_exist")
    
    installed_version = fields.Char("Installed Version", compute="_compute_versions",
                                    help="Version installed on Database")
    
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
    
    error_msg = fields.Char("Error")
    last_check = fields.Datetime("Last Check")
    
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
        
    @api.onchange('module_name')
    def _compute_module_icon(self):
        for rec in self:
            rec.module_icon = f"/{self.module_name}/static/description/icon.png"
    
    @api.depends('module_name','module_exist')
    def _compute_backup_ids(self):
        
        def search_or_create_Command(model,vals:dict):
            existing = model.search([(key,'=',value) for key,value in vals.items()] , limit=1)
            return Command.link(existing.id) if existing else Command.create(vals)
        
        for rec in self:
            rec.backup_ids = False
            if not rec.id:
                continue
            if rec.module_exist:
                backups = get_backup_list(rec.module_name,rec._get_module_local_path())
                backups.reverse()
                rec.backup_ids = [search_or_create_Command(rec.backup_ids,{
                        'name':backup_name,
                        'version': backup_version,
                        'size':backup_size,
                        'path':backup_path,
                        'e_update_id':f"{rec._name},{rec.id}",
                    }) for backup_name,backup_version,backup_size,backup_path in backups]
                    
                
    @api.depends('module_name')
    def _compute_module_exist(self):
        for rec in self:
            rec.module_exist = rec.module_name and  rec.env['ir.module.module'].search_count([('name','=',rec.module_name)]) != 0 or False
    
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
    
    def _get_module_local_path(self):
        self.ensure_one()
        return  modules.get_module_path(self.module_name)
        
    @api.depends('module_name')
    def _compute_versions(self):
        for rec in self:
            if not rec.module_exist:
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
            installed_version = module.latest_version
            
            rec.update({
                'local_version': local_version or _("Unknown"),
                'repository_version': repository_version or _("Unknown"),
                'installed_version':installed_version or _("Unknown"),
            })
            rec.compute_update_state(local_version,installed_version)
            
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
                update_state = 'to_downgrade'
                error_msg = _("Version is older than module's version")
        elif error_if_not_version:
            update_state = 'error'
            error_msg = error_if_not_version
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
            'name': _('Restart Server'),
            'type': 'ir.actions.act_window',
            'res_model': 'e_module_update.restart_server',
            'view_type': 'form',
            'view_mode': 'form',
            'view_ids': [('e_module_update.e_module_update_restart_server_view_form','form')],
            'target': 'new',
            'domain': [],
            'context': {
                'default_commands': self.env['ir.config_parameter'].get_param('e_module_update.command_restart_server',''),
            },
        }
        
    def action_create_backup(self):
        for rec in self:
            if rec.module_exist:
                make_backup(
                    rec._get_module_local_path(),
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
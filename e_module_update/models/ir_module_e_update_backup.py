from odoo import models,fields, Command , _ , exceptions
from ..utils.util import remove_backup , extract_zip_by_path , get_module_backups , get_all_backups
class EUpdateBackup(models.TransientModel):
    _name = 'ir.module.e_update.backup'
    _description = 'eUpdate Backup'
    
    name = fields.Char("Name")
    module_name = fields.Char("Module")
    version = fields.Char("Version")
    path = fields.Char("Path")
    size = fields.Char("Size")
    selected = fields.Boolean(string="Selected")
    
    def action_to_restore_model(self):
        MANUAL_MODEL = self.env['ir.module.e_update.manual']
        e_updata_manual =   MANUAL_MODEL.search(       
                                [('module_name','=',self.module_name)],limit=1  
                            ) or MANUAL_MODEL.create({
                                'module_name' : self.module_name
                            })
            
        return {
            'name': _('Backups'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.module.e_update.manual',
            'res_id': e_updata_manual.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'domain': [],
            'context': {
                'from_backup_list_view':True,
            },
        }
        
    def action_restore_backup(self):
        self.ensure_one()
        if not self.env.context.get('local_path'):
            raise exceptions.UserError(_("No local path provided"))
        
        extract_zip_by_path(
            self.path,
            self.env.context.get('local_path'),
            self.module_name,
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
        }
        
    def action_delete_backup(self):
        for rec in self:
            remove_backup(rec.path)
        if self.env.context.get('from_backup_list_view'):
            return self._get_backup_list_view()
        return {'type': 'ir.actions.act_window_close'}
        
        
    @staticmethod
    def _search_or_create_Command(env,vals:dict):
        existing = env['ir.module.e_update.backup'].search([(key,'=',value) for key,value in vals.items()] , limit=1)
        return Command.link(existing.id) if existing else Command.create(vals)
        
     
    @staticmethod
    def get_backups_Command(env, module_name , backups = False):
        if not backups:
            backups = get_module_backups(module_name)
            backups.reverse()
        return [EUpdateBackup._search_or_create_Command(env,{
                'name': backup_name,
                'version': backup_version,
                'size': backup_size,
                'path': backup_path,
                'module_name': backup_module,
            }) for backup_name,backup_version,backup_size,backup_path,backup_module in backups]
    
    def _get_backup_list_view(self):
        return {
            'name': _('Backups'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.module.e_update.backup',
            'view_type': 'list',
            'view_mode': 'list',
            'target': 'current',
            'domain': [],
            'context': {
                'from_backup_list_view':True,
            },
        }
    
    def action_load_backups(self):
        all_backups = get_all_backups()
        wanted_ids = []
        new_ids = []
        new_vals_list = []
        for module_name,backups in all_backups.items():
            commands = EUpdateBackup.get_backups_Command(self.env, module_name , backups)

            for cmd in commands:
                if cmd[0] == Command.CREATE:
                    new_vals_list.append(cmd[2]) 
                    
                elif cmd[0] == Command.LINK:
                    wanted_ids.append(cmd[1]) 

            for vals in new_vals_list:
                _new = self.env['ir.module.e_update.backup'].create(vals)
                new_ids.append(_new.id)
            
        self.env['ir.module.e_update.backup'].search([
            ('id', 'not in', wanted_ids + new_ids)
        ]).unlink()
        
        
        return self._get_backup_list_view()
        
        
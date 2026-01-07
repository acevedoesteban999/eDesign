from odoo import models,fields
from ..utils.util import remove_backup , extract_zip_by_path
class EUpdateBackup(models.TransientModel):
    _name = 'ir.module.e_update.backup'
    _description = 'eUpdate Backup'
    
    name = fields.Char("Name")
    version = fields.Char("Version")
    path = fields.Char("Path")
    size = fields.Char("Size")
    selected = fields.Boolean(string="Selected")
    e_update_id = fields.Reference([
            ('ir.module.e_update.manual',"Manual"),
        ],
    )   
    
    def action_restore_backup(self):
        self.ensure_one()
        extract_zip_by_path(
            self.path,
            self.e_update_id._get_module_local_path(),
            self.e_update_id.module_name,
        )
        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
        }
        
        
    def action_delete_backup(self):
        for rec in self:
            remove_backup(rec.path)
        return {'type': 'ir.actions.act_window_close'}
        
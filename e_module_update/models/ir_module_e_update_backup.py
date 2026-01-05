from odoo import models,fields
from ..utils.util import remove_backup
class EUpdateBackup(models.TransientModel):
    _name = 'ir.module.e_update.backup'
    _description = 'eUpdate Backup'
    
    name = fields.Char("Name")
    version = fields.Char("Version")
    path = fields.Char("Path")
    size = fields.Char("Size")
    selected = fields.Boolean(string="Selected")
    
    def action_restore_backup(self):
        self.ensure_one()
    
    def action_delete_backup(self):
        for rec in self:
            remove_backup(rec.path)
        return {'type': 'ir.actions.act_window_close'}
        
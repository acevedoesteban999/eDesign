from odoo import models,fields

class EUpdateBackup(models.TransientModel):
    _name = 'ir.module.e_update.backup'
    _description = 'model.technical.name'

    
    name = fields.Char("Name")
    version = fields.Char("Version")
    size = fields.Char("Size")
    
    
    def action_restore_backup(self):
        pass
    
    def action_delete_backup(self):
        pass
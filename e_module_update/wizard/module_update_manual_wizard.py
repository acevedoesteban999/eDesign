from odoo import models , fields , exceptions
import zipfile
import io
import shutil
import os
class ModuleUpdateManualWizard(models.TransientModel):
    _name = "e_module_update.module_update_manual_wizard"
    
    module_update_id = fields.Many2one('e_module_update.module.updater',required=True)
    zip_file = fields.Binary("Zip File")
    
    def action_upload(self):
        updater = self.env['e_module_update.module.updater']
        local_path = self.module_update_id._get_module_local_path()
        module_name = self.module_update_id.module_name
        backup_path = updater._get_backup_path(local_path,module_name)
        shutil.move(local_path, backup_path)
        os.makedirs(local_path, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(self.zip_file)) as zip_file:
            count_files = updater._process_zip(zip_file,module_name,local_path)
            if count_files == 0:
                raise exceptions.UserError("No files found")
        shutil.rmtree(backup_path)
        
# -*- coding: utf-8 -*-
# Copyright 2025 
# License LGPL-3

import os
import zipfile
import io
import base64
import ast
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
from ..utils.util import extract_zip, make_backup, remove_backup, restore_backup , get_zip_by_prefix

_logger = logging.getLogger(__name__)

class eIrModuleUpdateManual(models.Model):
    _name = 'ir.module.e_update.manual'
    _inherit = 'ir.module.e_update'
    _description = 'Manual Module Updater'

    store_local = fields.Boolean(compute="_compute_store_local")
    zip_version = fields.Char("ZIP Version", compute="_compute_state")
    file_zip = fields.Binary("File ZIP")
    
    
    @api.depends('repository_version','zip_version')
    def _compute_store_local(self):
        for rec in self:
            rec.store_local = self.compare_versions(rec.zip_version,rec.repository_version) 
    
    
    
    
    def _recompute_file_zip(self):
        if self.module_state == 'installed' and self.state != 'error':
            if not self.file_zip:
                self.state = self.zip_version = False
                self.error_msg = _("No ZIP file provided")
                return
            
            try:
                zip_data = base64.b64decode(self.with_context(bin_size=False).file_zip)
                zip_file = zipfile.ZipFile(io.BytesIO(zip_data), 'r')
                manifest_content = None
                manifest_name_in_zip = None
                
                candidates = [f"{self.module_name}/__manifest__.py", "__manifest__.py"]
                
                for candidate in candidates:
                    if candidate in zip_file.namelist():
                        manifest_content = zip_file.read(candidate).decode('utf-8')
                        manifest_name_in_zip = candidate
                        break
                
                if not manifest_content:
                    self.zip_version =  False
                    self.state = 'error'
                    self.error_msg = _("No manifest file found in ZIP. Expected module structure.")
                    
                    zip_file.close()
                    return
                
                manifest_dict = ast.literal_eval(manifest_content)
                zip_version = manifest_dict.get('version', False)
                
                expected_name = None
                if '/' in manifest_name_in_zip:
                    expected_name = manifest_name_in_zip.split('/')[0]
                else:
                    expected_name = self.module_name
                
                if expected_name != self.module_name:
                    self.zip_version = False
                    self.state ='error'
                    self.error_msg =_("Module name mismatch: ZIP contains '%s', expected '%s'") % (expected_name, self.module_name)
                    
                    zip_file.close()
                    return
                
                
                self.zip_version = zip_version
                
                zip_file.close()
                
            except zipfile.BadZipFile as e:
                self.zip_version = False
                self.state ='error'
                self.error_msg = _("Invalid ZIP file format: %s") % e
        
            except Exception as e:
                _logger.error("Error processing ZIP for module %s: %s", self.module_name, str(e))
                self.zip_version = False
                self.state ='error'
                self.error_msg = _("Error reading ZIP: %s") % str(e)
        else:
            self.state = False
            self.error_msg = False
            self.zip_version = False

    def _get_versions(self):
        versions = super()._get_versions() 
        if self.zip_version:
            versions = [self.zip_version] + versions
        return versions

    @api.depends('file_zip')
    def _compute_state(self):
        for rec in self:
            rec._recompute_file_zip()
            super(eIrModuleUpdateManual,rec)._compute_state()
                
    # ===================================================================
    # ACTIONS
    # ===================================================================

    def action_store_version(self):
        self.ensure_one()
        
        if not self.file_zip:
            raise UserError(_("No ZIP file provided"))

        if self.state not in ['to_update','to_downgrade']:
            raise UserError(_("Cannot update: %s") % (self.error_msg or _("Invalid state")))
        
        if not self.local_version:
            raise UserError(_("No local version provided"))
        
        local_path = self.local_path
        
        if not local_path:
            raise UserError(_("No local path provided"))
        
        backup_path = make_backup(
            local_path=local_path,
            module_name=self.module_name,
            version=self.local_version
        )
        
        try:
            zip_data = base64.b64decode(self.with_context(bin_size=False).file_zip)
            zip_file = zipfile.ZipFile(io.BytesIO(zip_data), 'r')
            
            top_items = set(name.split('/')[0] for name in zip_file.namelist() if name)
            if self.module_name in top_items:
                zip_for_extraction = get_zip_by_prefix(zip_file,self.module_name)
            else:
                zip_for_extraction = zip_file
                
            if "__manifest__.py" not in zip_for_extraction.namelist():
                raise UserError(_("No manifest provided"))
            upload_files = extract_zip(zip_for_extraction,local_path)
            
            if upload_files == 0:
                raise UserError(_("No files were extracted from the ZIP"))
            
            _logger.info("Module %s updated successfully: %d files extracted", self.module_name, upload_files)
                    
        except Exception as e:
            _logger.error("Update failed for %s: %s. Restoring backup from ZIP.", self.module_name, e)
            if backup_path and os.path.exists(backup_path):
                try:
                    restore_backup(backup_path, local_path,True)
                    _logger.info("Backup restored successfully from ZIP")
                except Exception as restore_error:
                    _logger.error("Failed to restore backup: %s", restore_error)
            
            raise UserError(_("Update failed: %s") % str(e))
        
        self._compute_state()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Module %s store successfully! Files updated: %d') % 
                            (self.module_name, upload_files),
                'type': 'success',
                'sticky': False,
                'next':{'type': 'ir.actions.act_window_close'}
            }
        }

    def action_open_addon_modules_wizard(self):
        return {
            'name': _('Import Modules to Update Manual'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'e_module_base.addon_modules_wizard',
            'views': [(self.env.ref('e_module_update.view_addon_modules_eupdate_manual_wizard_form').id,'form')],
            'domain': [],
            'context': {}
        }
        

     
                    
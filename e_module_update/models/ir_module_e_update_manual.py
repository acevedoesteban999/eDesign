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
from ..utils.util import copy_zip, make_backup, remove_backup, restore_backup , get_zip_by_prefix

_logger = logging.getLogger(__name__)

class eIrModuleUpdateManual(models.Model):
    _name = 'ir.module.e_update.manual'
    _inherit = 'ir.module.e_update'
    _description = 'Manual Module Updater'

    zip_version = fields.Char("ZIP Version", compute="_compute_versions",store=True)
    file_zip = fields.Binary("File ZIP")
    
    @api.depends('module_name','file_zip')
    def _compute_versions(self):
        for record in self:
            super(eIrModuleUpdateManual, record)._compute_versions()
            if record.module_exist:
                if not record.file_zip:
                    record.update({
                        'zip_version': _("Unknown"),
                        'update_state': 'error',
                        'error_msg': _("No ZIP file provided"),
                    })
                    continue
                
                try:
                    zip_data = base64.b64decode(record.with_context(bin_size=False).file_zip)
                    zip_file = zipfile.ZipFile(io.BytesIO(zip_data), 'r')
                    manifest_content = None
                    manifest_name_in_zip = None
                    
                    candidates = [f"{record.module_name}/__manifest__.py", "__manifest__.py"]
                    
                    for candidate in candidates:
                        if candidate in zip_file.namelist():
                            manifest_content = zip_file.read(candidate).decode('utf-8')
                            manifest_name_in_zip = candidate
                            break
                    
                    if not manifest_content:
                        record.update({
                            'zip_version': _("Unknown"),
                            'update_state': 'error',
                            'error_msg': _("No manifest file found in ZIP. Expected module structure."),
                        })
                        zip_file.close()
                        continue
                    
                    manifest_dict = ast.literal_eval(manifest_content)
                    zip_version = manifest_dict.get('version', _("Unknown"))
                    
                    expected_name = None
                    if '/' in manifest_name_in_zip:
                        expected_name = manifest_name_in_zip.split('/')[0]
                    else:
                        expected_name = record.module_name
                    
                    if expected_name != record.module_name:
                        record.update({
                            'zip_version': _("Unknown"),
                            'update_state': 'error',
                            'error_msg': _("Module name mismatch: ZIP contains '%s', expected '%s'") % 
                                    (expected_name, record.module_name),
                        })
                        zip_file.close()
                        continue
                    
                    self.compute_update_state(zip_version,self.local_version)
                    
                    record.update({
                        'zip_version': zip_version,
                    })
                    zip_file.close()
                    
                except zipfile.BadZipFile as e:
                    record.update({
                        'zip_version': _("Unknown"),
                        'update_state': 'error',
                        'error_msg': _("Invalid ZIP file format: %s") % e,
                    })
                except Exception as e:
                    _logger.error("Error processing ZIP for module %s: %s", record.module_name, str(e))
                    record.update({
                        'zip_version': _("Unknown"),
                        'update_state': 'error',
                        'error_msg': _("Error reading ZIP: %s") % str(e),
                    })

    def _update_from_zip(self):
        self.ensure_one()
        
        if not self.file_zip:
            raise UserError(_("No ZIP file provided"))
        
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
        
        try:
            zip_data = base64.b64decode(self.file_zip)
            zip_file = zipfile.ZipFile(io.BytesIO(zip_data), 'r')
            
            top_items = set(name.split('/')[0] for name in zip_file.namelist() if name)
            if len(top_items) == 1 and list(top_items)[0] == self.module_name:
                zip_for_extraction = get_zip_by_prefix(zip_file,self.module_name)
            else:
                zip_for_extraction = zip_file
            
            extracted_files = copy_zip(zip_for_extraction,local_path)
            
            if extracted_files == 0:
                raise UserError(_("No files were extracted from the ZIP"))
            
            _logger.info("Module %s updated successfully: %d files extracted", self.module_name, extracted_files)
            
            # remove_backup(backup_path)
            
            return extracted_files
            
        except Exception as e:
            _logger.error("Update failed for %s: %s. Restoring backup from ZIP.", self.module_name, e)
            if backup_path and os.path.exists(backup_path):
                try:
                    restore_backup(backup_path, local_path)
                    _logger.info("Backup restored successfully from ZIP")
                except Exception as restore_error:
                    _logger.error("Failed to restore backup: %s", restore_error)
            
            raise UserError(_("Update failed: %s") % str(e))
        
        finally:
            zip_file.close()

    # ===================================================================
    # ACTIONS
    # ===================================================================

    def action_store_version(self):
        self.ensure_one()
        
        try:
            downloaded_files = self._update_from_zip()
            self._compute_versions()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Module %s updated successfully!\nNew version: %s\nFiles updated: %d') % 
                              (self.module_name, self.zip_version, downloaded_files),
                    'type': 'success',
                    'sticky': False,
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
        except Exception as e:
            _logger.exception("Update failed for module %s", self.module_name)
            self._compute_versions()
            raise UserError(_("Update failed: %s") % str(e))

    
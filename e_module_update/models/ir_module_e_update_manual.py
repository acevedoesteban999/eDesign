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
    zip_version = fields.Char("ZIP Version", compute="_compute_versions")
    file_zip = fields.Binary("File ZIP")
    
    
    @api.depends('repository_version','zip_version')
    def _compute_store_local(self):
        for rec in self:
            rec.store_local = self.compare_versions(rec.zip_version,rec.repository_version) 
    
    
    
    @api.depends('module_name','file_zip')
    def _compute_versions(self):
        for rec in self:
            super(eIrModuleUpdateManual, rec)._compute_versions(False)
            if rec.module_exist and rec.update_state != 'error':
                if not rec.file_zip:
                    rec.update({
                        'zip_version': _("Unknown"),
                        'update_state': 'error',
                        'error_msg': _("No ZIP file provided"),
                    })
                    continue
                
                try:
                    zip_data = base64.b64decode(rec.with_context(bin_size=False).file_zip)
                    zip_file = zipfile.ZipFile(io.BytesIO(zip_data), 'r')
                    manifest_content = None
                    manifest_name_in_zip = None
                    
                    candidates = [f"{rec.module_name}/__manifest__.py", "__manifest__.py"]
                    
                    for candidate in candidates:
                        if candidate in zip_file.namelist():
                            manifest_content = zip_file.read(candidate).decode('utf-8')
                            manifest_name_in_zip = candidate
                            break
                    
                    if not manifest_content:
                        rec.update({
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
                        expected_name = rec.module_name
                    
                    if expected_name != rec.module_name:
                        rec.update({
                            'zip_version': _("Unknown"),
                            'update_state': 'error',
                            'error_msg': _("Module name mismatch: ZIP contains '%s', expected '%s'") % 
                                    (expected_name, rec.module_name),
                        })
                        zip_file.close()
                        continue
                    
                    
                    rec.update({
                        'zip_version': zip_version,
                    })
                    
                    rec.compute_update_state()
                    
                    zip_file.close()
                    
                except zipfile.BadZipFile as e:
                    rec.update({
                        'zip_version': _("Unknown"),
                        'update_state': 'error',
                        'error_msg': _("Invalid ZIP file format: %s") % e,
                    })
                except Exception as e:
                    _logger.error("Error processing ZIP for module %s: %s", rec.module_name, str(e))
                    rec.update({
                        'zip_version': _("Unknown"),
                        'update_state': 'error',
                        'error_msg': _("Error reading ZIP: %s") % str(e),
                    })
            else:
                rec.zip_version = _("Unknown")

    def compute_update_state(self):
        self._compute_update_state(self.zip_version,self.repository_version)
        if not self.update_state or self.update_state == 'uptodate':
            super().compute_update_state()
    
    # ===================================================================
    # ACTIONS
    # ===================================================================

    def action_store_version(self):
        self.ensure_one()
        
        if not self.file_zip:
            raise UserError(_("No ZIP file provided"))

        if self.update_state not in ['to_update','to_downgrade']:
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
        
        self._compute_versions()
        
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

    
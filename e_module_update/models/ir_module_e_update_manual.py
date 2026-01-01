# -*- coding: utf-8 -*-
# Copyright 2025 
# License LGPL-3

import os
import requests
import base64
import zipfile
import io
from odoo import models, fields, api, _ 
from odoo.exceptions import UserError
import logging
from ..utils.util import process_zip , make_backup , remove_backup , restore_backup
_logger = logging.getLogger(__name__)

class eIrModuleUpdateManual(models.Model):
    _name = 'ir.module.e_update.manual'
    _inherit = 'ir.module.e_update'
    _description = 'GitHub Module Updater'

    zip_version = fields.Char("Remote Version", compute="_compute_versions")
    file_zip = fields.Binary("File zip", store=False)
    remote_state = fields.Selection([
        ('uptodate',"Uptodate"),
        ('to_update',"To Update"),
        ('error',"Error"),
        ], compute="_compute_versions",default="error")
    error = fields.Char("Error")
    
    def _get_zip_version(self):
        self.ensure_one()
        


    # ===================================================================
    # ACTIONS
    # ===================================================================

    def action_confirm_and_update(self):
        self.ensure_one()
        
        try:
            if self.env.context.get("download_by_zip"):
                downloaded_files = self._download_entire_subfolder_zip()
            else:
                downloaded_files = self._download_entire_subfolder_optimized()
            self._compute_versions()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Module updated successfully from GitHub!\nNew version: %s! Downloaded : %s files') % (self.remote_version,str(downloaded_files)),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            _logger.exception("Update failed for module %s", self.module_name)
            raise UserError(_("Update failed: %s") % str(e))

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
from ..utils.util import copy_zip , make_backup , remove_backup , restore_backup , get_zip_by_prefix
_logger = logging.getLogger(__name__)

class eIrModuleUpdateGit(models.Model):
    _name = 'ir.module.e_update.git'
    _inherit = 'ir.module.e_update'
    _description = 'Git Module Updater'

    repo_url = fields.Char("GitHub Repo URL",help="e.g., https://github.com/odoo/odoo", required=True)
    
    subfolder_path = fields.Char("Subfolder Path", required=True)
    branch = fields.Char("Branch", default="main", required=True)
    remote_version = fields.Char("Remote Version", compute="_compute_versions",store=True)
    
    def _get_remote_git_version(self):
        self.ensure_one()
        
        url_parts = self.repo_url.rstrip('/').split('/')
        owner, repo = url_parts[-2], url_parts[-1].replace('.git', '')
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{self.subfolder_path or self.module_name}/__manifest__.py"
        params = {'ref': self.branch}
        
        try:
            response = requests.get(
                api_url, 
                headers=self._get_github_api_headers(),
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                file_data = response.json()
                content = base64.b64decode(file_data['content']).decode('utf-8')
                manifest_dict = eval(content, {'__builtins__': {}}, {})
                return manifest_dict.get('version', False) , False
                
        except requests.exceptions.RequestException as e:
            _logger.error("GitHub API error for %s: %s", self.module_name, e)
            return False , str(e)
        
        return False , f"Code: {response.status_code} ; Reason: {response.reason}"
    
    
    def _download_entire_subfolder_zip(self):
        self.ensure_one()
        
        url_parts = self.repo_url.rstrip('/').split('/')
        owner, repo = url_parts[-2], url_parts[-1].replace('.git', '')
        
        local_path = self._get_module_local_path()
        if not local_path:
            raise UserError(_("Local module path not found. Is the module installed?"))
        
        backup_path = make_backup(local_path,self.module_name)
        
        try:
            zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{self.branch}.zip"
            _logger.info("Downloading ZIP from: %s", zip_url)
            
            response = requests.get(zip_url, timeout=300)
            if response.status_code != 200:
                raise UserError(_("Failed to download ZIP: HTTP %s") % response.status_code)
            
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                prefix = f"{repo}-{self.branch}/{self.subfolder_path}/"
                zip_for_extraction = get_zip_by_prefix(zip_file,prefix)
                extracted_files = copy_zip(zip_for_extraction,prefix,local_path)
                if extracted_files == 0:
                    raise UserError(_("No files found in subfolder: %s") % self.subfolder_path)
                _logger.info("Extracted %d files to %s", extracted_files, local_path)   
            remove_backup(backup_path)
            _logger.info("Successfully updated module %s from GitHub", self.module_name)
            return extracted_files
        except Exception as e:
            _logger.error("Update failed for %s: %s. Restoring backup.", self.module_name, e)
            restore_backup(backup_path,local_path,True)
            raise UserError(_("Update failed: %s") % str(e))
    
    def _download_entire_subfolder_optimized(self):
        self.ensure_one()
        
        url_parts = self.repo_url.rstrip('/').split('/')
        owner, repo = url_parts[-2], url_parts[-1].replace('.git', '')
        
        local_path = self._get_module_local_path()
        if not local_path:
            raise UserError(_("Local module path not found. Is the module installed?"))
        
        backup_path = make_backup(local_path , self.module_name)
        
        try:
            api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{self.branch}?recursive=1"
            headers = self._get_github_api_headers()
            
            tree_response = requests.get(api_url, headers=headers, timeout=30)
            if tree_response.status_code != 200:
                raise UserError(_("GitHub API error %s: %s") % (tree_response.status_code, tree_response.text))
            
            tree_data = tree_response.json()
            files_to_download = []
            
            subfolder_prefix = self.subfolder_path.rstrip('/') + '/'
            for item in tree_data.get('tree', []):
                if item['type'] == 'blob' and item['path'].startswith(subfolder_prefix):
                    relative_path = item['path'][len(subfolder_prefix):]
                    if relative_path: 
                        files_to_download.append({
                            'path': relative_path,
                            'sha': item['sha']
                        })
            
            if not files_to_download:
                raise UserError(_("No files found in subfolder: %s") % self.subfolder_path)
            
            base_raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{self.branch}/{self.subfolder_path}"
            downloaded_files = 0
            
            for file_info in files_to_download:
                target_path = os.path.join(local_path, file_info['path'])
                raw_url = f"{base_raw_url}/{file_info['path']}"
                
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                file_response = requests.get(raw_url, timeout=60)
                
                if file_response.status_code == 200:
                    with open(target_path, 'wb') as f:
                        f.write(file_response.content)
                    downloaded_files += 1
                else:
                    _logger.warning("Failed to download %s (HTTP %s)", raw_url, file_response.status_code)
            
            _logger.info("Downloaded %d files to %s", downloaded_files, local_path)
            
            remove_backup(backup_path)
            return downloaded_files
            
        except Exception as e:
            _logger.error("Update failed for %s: %s. Restoring backup.", self.module_name, e)
            restore_backup(backup_path, local_path)
            raise UserError(_("Update failed: %s") % str(e))

    @api.depends('repo_url', 'subfolder_path', 'branch')
    def _compute_versions(self):
        for record in self:
            super(record,eIrModuleUpdateGit)._compute_versions()
            remote_version , remote_error = record._get_remote_git_version()
            
            self.compute_update_state(remote_version,self.local_version,remote_error)
            
            record.update({
                'remote_version': remote_version or "Unknown",
            })

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

    def action_check_repositiry(self):
        pass
    

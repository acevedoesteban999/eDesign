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
from odoo.modules.module import load_manifest
from ..utils.util import extract_zip_by_prefix , extract_zip , make_backup , remove_backup , restore_backup
_logger = logging.getLogger(__name__)

class eIrModuleUpdateGitRemote(models.Model):
    _name = 'ir.module.e_update.git.remote'
    _inherit = 'ir.module.e_update'
    _description = 'Git Remote Module Updater'

    repo_url = fields.Char("GitHub Repo URL",help="e.g., https://github.com/odoo/odoo", required=True)
    
    subfolder_path = fields.Char("Subfolder Path", required=True)
    branch = fields.Char("Branch", default="main", required=True)
    remote_version = fields.Char("Remote Version", compute="_compute_versions")
    download_local = fields.Boolean(compute="_compute_download_local")
    git_remote = fields.Selection([
        ('github',"GitHub"),
    ],default='github',required=True)
    
    def _get_github_api_headers(self):
        return {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Odoo-GitHub-Updater'
        }

    @api.depends('repository_version','remote_version')
    def _compute_download_local(self):
        for rec in self:
            rec.download_local = self.compare_versions(rec.remote_version,rec.repository_version) 
    
    def _get_remote_git_version(self):
        self.ensure_one()
        
        url_parts = self.repo_url.rstrip('/').split('/')
        owner, repo = url_parts[-2], url_parts[-1].replace('.git', '')
        
        if self.subfolder_path:
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{self.subfolder_path}/__manifest__.py"
        else:
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/__manifest__.py"
        
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
        
        return False , "%s: %s" % (response.status_code,response.reason)
    
    def _download_entire_subfolder_zip(self):
        self.ensure_one()
        
        url_parts = self.repo_url.rstrip('/').split('/')
        owner, repo = url_parts[-2], url_parts[-1].replace('.git', '')
        
        local_path = self.local_path
        if not local_path:
            raise UserError(_("Local module path not found. Is the module installed?"))
        
        backup_path = make_backup(local_path,self.module_name,self.local_version)
        
        try:
            zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{self.branch}.zip"
            _logger.info("Downloading ZIP from: %s", zip_url)
            
            response = requests.get(zip_url, timeout=300)
            if response.status_code != 200:
                raise UserError(_("Failed to download ZIP: HTTP %s") % response.status_code)
            
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                prefix = f"{repo}-{self.branch}/{self.subfolder_path}"
                extracted_files = extract_zip_by_prefix(zip_file,local_path,prefix)
                if extracted_files == 0:
                    raise UserError(_("No files found in subfolder: %s") % self.subfolder_path)
                _logger.info("Extracted %d files to %s", extracted_files, local_path)   
           
            _logger.info("Successfully updated module %s from GitHub", self.module_name)
            return extracted_files
        except Exception as e:
            _logger.error("Update failed for %s: %s. Restoring backup.", self.module_name, e)
            restore_backup(backup_path,local_path,True)
            raise UserError(_("Update failed: %s") % str(e))
    
    def _download_entire_subfolder_raw(self):
        self.ensure_one()

        url_parts = self.repo_url.rstrip('/').split('/')
        owner, repo = url_parts[-2], url_parts[-1].replace('.git', '')

        local_path = self.local_path
        if not local_path:
            raise UserError(_("Local module path not found. Is the module installed?"))

        backup_path = make_backup(local_path, self.module_name, self.local_version)
        try:
            api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{self.branch}?recursive=1"
            headers = self._get_github_api_headers()

            tree_rsp = requests.get(api_url, headers=headers, timeout=30)
            if tree_rsp.status_code != 200:
                raise UserError(_("GitHub API error %s: %s") % (tree_rsp.status_code, tree_rsp.text))

            tree_data = tree_rsp.json()
            sub_prefix = self.subfolder_path.rstrip('/') + '/'

            files_to_download = [
                item['path'][len(sub_prefix):]
                for item in tree_data.get('tree', [])
                if item['type'] == 'blob' and item['path'].startswith(sub_prefix)
            ]
            if not files_to_download:
                raise UserError(_("No files found in subfolder: %s") % self.subfolder_path)

            zip_buffer = io.BytesIO()    
            base_raw = f"https://raw.githubusercontent.com/{owner}/{repo}/{self.branch}/{self.subfolder_path}"

            with zipfile.ZipFile(zip_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
                for rel_path in files_to_download:
                    raw_url = f"{base_raw}/{rel_path}"
                    file_rsp = requests.get(raw_url, timeout=60)
                    if file_rsp.status_code != 200:
                        raise UserError(
                            _("Failed to download %(path)s (HTTP %(status)s)")
                            % {'path': rel_path, 'status': file_rsp.status_code}
                        )
                    zf.writestr(rel_path, file_rsp.content)

            zip_buffer.seek(0)
            with zipfile.ZipFile(zip_buffer) as zf:
                extracted = extract_zip(zf, local_path)
            

            _logger.info("Extracted %d files to %s", extracted, local_path)
            return extracted
        except Exception as e:
            _logger.error("Update failed for %s: %s. Restoring backup.", self.module_name, e)
            restore_backup(backup_path,local_path,True)
            raise UserError(_("Update failed: %s") % str(e))

    @api.depends('repo_url', 'subfolder_path', 'branch')
    def _compute_versions(self):
        for rec in self:
            super(eIrModuleUpdateGitRemote,rec)._compute_versions(False)
            
            if rec.module_exist and rec.update_state != 'error':
                if not rec.repo_url:
                    rec.update({
                        'remote_version': _("Unknown"),
                        'update_state': 'error',
                        'error_msg': _("No Repository URL Provided"),
                    })
                    continue
                
                remote_version , remote_error = rec._get_remote_git_version()
                
            
                rec.write({
                    'remote_version': remote_version or "Unknown",
                })
                
                self.compute_update_state(remote_error)
            else:
                rec.remote_version = _("Unknown")

    def compute_update_state(self,remote_error=False):
        self._compute_update_state(self.remote_version,self.repository_version)
        if remote_error and not self.update_state:
            self.update_state = 'error'
            self.error_msg = remote_error
        elif not self.update_state or self.update_state == 'uptodate':
            super().compute_update_state()
    
    # ===================================================================
    # ACTIONS
    # ===================================================================

    def action_download_zip_version(self):
        self.ensure_one()
        
        try:
            downloaded_files = self._download_entire_subfolder_zip()
            self._compute_versions()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Module updated successfully from GitHub!\nNew version: %s! Downloaded : %s files') % (self.remote_version,str(downloaded_files)),
                    'type': 'success',
                    'sticky': False,
                    'next':{
                        'type': 'ir.actions.act_window_close'
                    }
                },
            }
        except Exception as e:
            _logger.exception("Update failed for module %s", self.module_name)
            raise UserError(_("Update failed: %s") % str(e))

    def action_download_raw_version(self):
        self.ensure_one()
        
        try:
            downloaded_files = self._download_entire_subfolder_raw()
            self._compute_versions()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Module updated successfully from GitHub!\nNew version: %s! Downloaded : %s files') % (self.remote_version,str(downloaded_files)),
                    'type': 'success',
                    'sticky': False,
                    'next':{
                        'type': 'ir.actions.act_window_close'
                    }
                        
                }
            }
        except Exception as e:
            _logger.exception("Update failed for module %s", self.module_name)
            raise UserError(_("Update failed: %s") % str(e))

    
    

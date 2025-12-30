# -*- coding: utf-8 -*-
# Copyright 2025 
# License LGPL-3

import os
import shutil
import requests
import base64
import zipfile
import io
from odoo import models, fields, api, _ , modules
from odoo.modules import get_manifest
import hashlib
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class EGithubModuleUpdater(models.Model):
    _name = 'e_module_update.module.updater'
    _description = 'GitHub Module Updater'
    _rec_name = 'module_name'

    # CONFIGURACIÓN
    module_name = fields.Char("Module Technical Name", required=True)
    repo_url = fields.Char("GitHub Repo URL", 
                          help="e.g., https://github.com/odoo/odoo", required=True)
    subfolder_path = fields.Char("Subfolder Path", 
                                help="e.g., addons/mail", required=True)
    branch = fields.Char("Branch", default="main", required=True)
    
    # INFORMACIÓN (solo lectura)
    local_version = fields.Char("Local Version", compute="_compute_versions")
    installed_version = fields.Char("Installed Version", compute="_compute_versions")
    remote_version = fields.Char("Remote Version", compute="_compute_versions")
    last_check = fields.Datetime("Last Check")
    
    # ESTADO
    remote_state = fields.Selection([
        ('uptodate',"Uptodate"),
        ('to_update',"To Update"),
        ('error',"Error"),
        ], compute="_compute_versions",default="error")
    error = fields.Char("Error")
    _sql_constraints = [
        ('unique_module', 'unique(module_name)', 'Module must be unique!')
    ]

    # ===================================================================
    # MÉTODOS PRINCIPALES (GITHUB API)
    # ===================================================================

    def _get_github_api_headers(self):
        """Headers para GitHub API (público, sin auth)"""
        return {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Odoo-GitHub-Updater'
        }

    def _get_module_git_version(self):
        """Lee __manifest__.py directamente desde GitHub API"""
        self.ensure_one()
        
        # Construir URL de la API para el archivo
        # Formato: /repos/{owner}/{repo}/contents/{path}
        url_parts = self.repo_url.rstrip('/').split('/')
        owner, repo = url_parts[-2], url_parts[-1].replace('.git', '')
        
        # Intentar __manifest__.py primero
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
                # El contenido está en base64
                content = base64.b64decode(file_data['content']).decode('utf-8')
                # Evaluar de forma segura
                manifest_dict = eval(content, {'__builtins__': {}}, {})
                return manifest_dict.get('version', False) , False
                
        except requests.exceptions.RequestException as e:
            _logger.error("GitHub API error for %s: %s", self.module_name, e)
            return False , str(e)
        
        return False , f"Code: {response.status_code} ; Reason: {response.reason}"

    def _get_module_local_path(self):
        self.ensure_one()
        return  modules.get_module_path(self.module_name)
    
    def _get_module_local_version(self):
        self.ensure_one()
        return get_manifest(self.module_name).get('version')
        
    def _download_entire_subfolder(self):
        """Descarga TODA la subcarpeta desde GitHub ZIP y reemplaza el contenido local"""
        self.ensure_one()
        
        # 1. Obtener datos del repositorio
        url_parts = self.repo_url.rstrip('/').split('/')
        owner, repo = url_parts[-2], url_parts[-1].replace('.git', '')
        
        local_path = self._get_module_local_path()
        if not local_path:
            raise UserError(_("Local module path not found. Is the module installed?"))
        
        backup_path = local_path + '.backup_' + fields.Datetime.now().strftime('%Y%m%d_%H%M%S')
        shutil.move(local_path, backup_path)
        os.makedirs(local_path, exist_ok=True)
        
        try:
            zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{self.branch}.zip"
            _logger.info("Downloading ZIP from: %s", zip_url)
            
            response = requests.get(zip_url, timeout=300)
            if response.status_code != 200:
                raise UserError(_("Failed to download ZIP: HTTP %s") % response.status_code)
            
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                prefix = f"{repo}-{self.branch}/{self.subfolder_path}/"
                
                extracted_files = 0
                for zip_info in zip_file.infolist():
                    if zip_info.filename.startswith(prefix) and not zip_info.is_dir():
                        relative_path = zip_info.filename[len(prefix):]
                        if relative_path: 
                            target_path = os.path.join(local_path, relative_path)
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            
                            with zip_file.open(zip_info) as source, open(target_path, 'wb') as target:
                                shutil.copyfileobj(source, target)
                            extracted_files += 1
                
                if extracted_files == 0:
                    raise UserError(_("No files found in subfolder: %s") % self.subfolder_path)
                
                _logger.info("Extracted %d files to %s", extracted_files, local_path)
            
            shutil.rmtree(backup_path)
            _logger.info("Successfully updated module %s from GitHub", self.module_name)
            return extracted_files
        except Exception as e:
            _logger.error("Update failed for %s: %s. Restoring backup.", self.module_name, e)
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
            shutil.move(backup_path, local_path)
            raise UserError(_("Update failed: %s") % str(e))
    
    

    def _download_entire_subfolder_optimized(self):
        self.ensure_one()
        
        url_parts = self.repo_url.rstrip('/').split('/')
        owner, repo = url_parts[-2], url_parts[-1].replace('.git', '')
        
        local_path = self._get_module_local_path()
        if not local_path:
            raise UserError(_("Local module path not found. Is the module installed?"))
        
        backup_path = local_path + '.backup_' + fields.Datetime.now().strftime('%Y%m%d_%H%M%S')
        shutil.move(local_path, backup_path)
        os.makedirs(local_path, exist_ok=True)
        
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
            
            shutil.rmtree(backup_path)
            return downloaded_files
            
        except Exception as e:
            _logger.error("Update failed for %s: %s. Restoring backup.", self.module_name, e)
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
            shutil.move(backup_path, local_path)
            raise UserError(_("Update failed: %s") % str(e))

    
    @api.depends('module_name', 'repo_url', 'subfolder_path', 'branch')
    def _compute_versions(self):
        """Computa versión local vs remota"""
        for record in self:
            if not record.module_name:
                record.update({
                    'local_version': 'Unknown',
                    'remote_version': 'Unknown',
                    'installed_version': 'Unknown',
                })
                continue
            
            # local_path = record._get_module_local_path()
            local_version = record._get_module_local_version()
            installed_version = self.env['ir.module.module'].search([('name','=',self.module_name)]).installed_version
            
            remote_version , remote_error = record._get_module_git_version()
            
            if not remote_version and remote_error:
                remote_state = 'error'
                error = remote_error
            elif not local_version:
                remote_state = 'error'
                error = "Unknown Local Version"
            elif not installed_version:
                remote_state = 'error'
                error = "Unknown Installed Version"
            elif local_version == remote_version:
                remote_state = 'uptodate'
                error = ""
            else:
                remote_state = 'to_update'
                error = ""
            
            record.update({
                'local_version': local_version or "Unknown",
                'installed_version':installed_version or "Unknown",
                'remote_version': remote_version or "Unknown",
                'error': error,
                'remote_state': remote_state,
                'last_check': fields.Datetime.now(),
            })

    # ===================================================================
    # ACCIONES
    # ===================================================================

    def action_check_version(self):
        """Acción manual: verificar versión remota"""
        self.ensure_one()
        self._compute_versions()
        
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Version Check'),
                'type': 'info',
                'sticky': False,
            }
        }
        

    def action_confirm_and_update(self):
        """Confirma y ejecuta la actualización"""
        self.ensure_one()
        
        try:
            if self.env.context.get("download_by_zip"):
                downloaded_files = self._download_entire_subfolder()
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

    
    def action_update_local_module(self):
        pass
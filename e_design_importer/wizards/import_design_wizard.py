import os
import base64
from pathlib import Path

from odoo import models, fields, api, _
from odoo.exceptions import UserError

from ..utils.utils import FolderScanner


class ImportDesignWizard(models.TransientModel):
    _name = 'import.design.wizard'
    _description = 'Import Design Wizard'
    
    folder_path = fields.Char(string='Desktop Folder Path', required=True, default="E:\Esteban\Programacion\Python\Odoo\Odoo18\designs")
    preview_data = fields.Json(string='Preview Data', default=dict)
    state = fields.Selection([
        ('select', 'Select Folder'),
        ('preview', 'Preview'),
        ('done', 'Done')
    ], default='select')
    
    def action_scan_folder(self):
        self.ensure_one()
        if not os.path.exists(self.folder_path):
            raise UserError(_('Folder does not exist: %s') % self.folder_path)
        
        scanner = FolderScanner(self.folder_path)
        data = scanner.scan()
        
        data['existing'] = {
            'categories': [],
            'subcategories': [],
            'designs': [],
            'products': []
        }
        
        for cat in data['categories']:
            existing = self.env['product.edesign.category'].search([
                ('default_code', '=', cat['code'])
            ], limit=1)
            if existing:
                data['existing']['categories'].append({
                    'code': cat['code'],
                    'name': existing.name,
                    'id': existing.id
                })
        
        for sub in data['subcategories']:
            existing = self.env['product.edesign.category'].search([
                ('default_code', '=', sub['code'])
            ], limit=1)
            if existing:
                data['existing']['subcategories'].append({
                    'code': sub['code'],
                    'name': existing.name,
                    'id': existing.id
                })
        
        for des in data['designs']:
            existing = self.env['product.edesign'].search([
                ('default_code', '=', des['code'])
            ], limit=1)
            if existing:
                data['existing']['designs'].append({
                    'code': des['code'],
                    'name': existing.name,
                    'id': existing.id
                })
        
        for prod in data['products']:
            existing = self.env['product.template'].search([
                ('default_code', '=', prod['code'])
            ], limit=1)
            if existing:
                data['existing']['products'].append({
                    'code': prod['code'],
                    'name': existing.name,
                    'id': existing.id
                })
        
        self.write({
            'preview_data': data,
            'state': 'preview'
        })
        
        return self._reload_wizard()
    
    def action_confirm_import(self):
        self.ensure_one()
        scanner = FolderScanner(self.folder_path)
        data = scanner.scan()
        
        category_map = {}
        for cat_data in data['categories']:
            cat = self.env['product.edesign.category'].search([('default_code', '=', cat_data['code'])], limit=1)
            if not cat:
                cat = self.env['product.edesign.category'].create({
                    'name': cat_data['name'],
                    'default_code': cat_data['code']
                })
            category_map[cat_data['code']] = cat.id
        
        for sub_data in data['subcategories']:
            sub = self.env['product.edesign.category'].search([('default_code', '=', sub_data['code'])], limit=1)
            if not sub:
                sub = self.env['product.edesign.category'].create({
                    'name': sub_data['name'],
                    'default_code': sub_data['code'],
                    'parent_id': category_map.get(sub_data['parent_code'])
                })
                category_map[sub_data['code']] = sub.id
        
        for design_data in data['designs']:
            existing = self.env['product.edesign'].search([('default_code', '=', design_data['code'])], limit=1)
            if not existing:
                attachments = self._process_attachments(design_data['path'])
                self.env['product.edesign'].create({
                    'name': design_data['name'],
                    'default_code': design_data['code'],
                    'category_id': category_map.get(design_data['category_code']),
                    'attachment_ids': [(6, 0, attachments)]
                })
        
        for prod_data in data['products']:
            product = self.env['product.template'].search([('default_code', '=', prod_data['code'])], limit=1)
            design_ids = []
            for d in prod_data['designs']:
                design = self.env['product.edesign'].search([('default_code', '=', d['code'])], limit=1)
                if design:
                    design_ids.append(design.id)
            
            if product:
                product.write({
                    'design_ok': True,
                    'design_ids': [(6, 0, design_ids)]
                })
            else:
                self.env['product.template'].create({
                    'name': prod_data['name'],
                    'default_code': prod_data['code'],
                    'design_ok': True,
                    'design_ids': [(6, 0, design_ids)]
                })
        
        self.state = 'done'
        return self._reload_wizard()
    
    def _process_attachments(self, folder_path):
        attachment_ids = []
        attachments_folder = os.path.join(folder_path, 'attachments')
        
        if not os.path.exists(attachments_folder):
            attachments_folder = os.path.join(folder_path, 'adjuntos')
        
        if os.path.exists(attachments_folder):
            for filename in os.listdir(attachments_folder):
                file_path = os.path.join(attachments_folder, filename)
                if not os.path.isfile(file_path):
                    continue
                    
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                if size_mb > 200:
                    continue
                
                with open(file_path, 'rb') as f:
                    data = base64.b64encode(f.read())
                    attachment = self.env['ir.attachment'].create({
                        'name': filename,
                        'datas': data,
                        'res_model': 'product.edesign',
                        'type': 'binary'
                    })
                    attachment_ids.append(attachment.id)
        
        image_path = os.path.join(folder_path, 'image.png')
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                data = base64.b64encode(f.read())
                attachment = self.env['ir.attachment'].create({
                    'name': 'image.png',
                    'datas': data,
                    'res_model': 'product.edesign',
                    'type': 'binary'
                })
                attachment_ids.append(attachment.id)
        
        return attachment_ids
    
    def action_back(self):
        self.write({'state': 'select', 'preview_data': {}})
        return self._reload_wizard()
    
    def _reload_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
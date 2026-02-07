import os
import base64
from pathlib import Path

from odoo import models, fields, api, _ , Command
from odoo.exceptions import UserError

from ..utils.utils import FolderScanner


class ImportDesignWizard(models.TransientModel):
    _name = 'import.design.wizard'
    _description = 'Import Design Wizard'
    
    folder_path = fields.Char(string='Desktop Folder Path', required=True, default="E:\\Esteban\\Programacion\\Python\\Odoo\\Odoo18\\designs")
    preview_data = fields.Json(string='Preview Data', default=dict)
    state = fields.Selection([
        ('select', 'Select Folder'),
        ('preview', 'Preview'),
    ], default='select')
    
    def action_scan_folder(self):
        self.ensure_one()
        if not os.path.exists(self.folder_path):
            raise UserError(_('Folder does not exist: %s') % self.folder_path)
        
        scanner = FolderScanner(self.folder_path)
        data = scanner.scan()
        
        def check_design(des):
            if not des:
                return None
            existing_des = self.env['product.edesign'].search([
                ('default_code', '=', des['code'])
            ], limit=1)
            result = {
                'name': des['name'],
                'code': des['code'],
                'path': des['path'],
                'image': des.get('image'),
                'file': des.get('file'),
                'attachments': des.get('attachments', []),
                'id': existing_des.id
            }
            return result
        
        def check_product(prod):
            if not prod:
                return None
            existing_prod = self.env['product.template'].search([
                ('default_code', '=', prod['code']),
                ('design_ok', '=', True)
            ], limit=1)
            result = {
                'name': prod['name'],
                'code': prod['code'],
                'path': prod['path'],
                'id': existing_prod.id,
                'designs': []
            }
            for des in prod.get('designs', []):
                checked_des = check_design(des)
                if checked_des:
                    result['designs'].append(checked_des)
            return result
        
        def check_subcategory(sub):
            if not sub:
                return None
            existing_sub = self.env['product.edesign.category'].search([
                ('default_code', '=', sub['code'])
            ], limit=1)
            result = {
                'name': sub['name'],
                'code': sub['code'],
                'path': sub['path'],
                'id': existing_sub.id,
                'products': [],
                'designs': []
            }
            if existing_sub:
                result['existing'] = {
                    'name': existing_sub.name,
                    'id': existing_sub.id
                }
              
            for prod in sub.get('products', []):
                checked_prod = check_product(prod)
                if checked_prod:
                    result['products'].append(checked_prod)
            for des in sub.get('designs', []):
                checked_des = check_design(des)
                if checked_des:
                    result['designs'].append(checked_des)
            
            return result
        
        def check_category(cat):
            if not cat:
                return None
            existing_cat = self.env['product.edesign.category'].search([
                ('default_code', '=', cat['code'])
            ], limit=1)
            result = {
                'name': cat['name'],
                'code': cat['code'],
                'path': cat['path'],
                'subcategories': [],
                'products': [],
                'designs': []
            }
            
            if existing_cat:
                result['existing'] = {
                    'name': existing_cat.name,
                    'id': existing_cat.id
                }
                
            for sub in cat.get('subcategories', []):
                checked_sub = check_subcategory(sub)
                if checked_sub:
                    result['subcategories'].append(checked_sub)
            for prod in cat.get('products', []):
                checked_prod = check_product(prod)
                if checked_prod:
                    result['products'].append(checked_prod)
            for des in cat.get('designs', []):
                checked_des = check_design(des)
                if checked_des:
                    result['designs'].append(checked_des)
            
            return result
        
        preview_data = {
            'categories': [],
            'products': [],
            'designs': []
        }
        
        for cat in data.get('categories', []):
            checked_cat = check_category(cat)
            if checked_cat:
                preview_data['categories'].append(checked_cat)
        
        for prod in data.get('products', []):
            checked_prod = check_product(prod)
            if checked_prod:
                preview_data['products'].append(checked_prod)
        
        for des in data.get('designs', []):
            checked_des = check_design(des)
            if checked_des:
                preview_data['designs'].append(checked_des)
        
        
        self.write({
            'preview_data': preview_data,
            'state': 'preview'
        })
        
        return self._reload_wizard()
    
    def action_confirm_import(self):
        self.ensure_one()
        
        preview_data = self.preview_data
        
        created_designs = 0
        
        def process_category(cat_data):
            cat_id = cat_data.get('id',False)
                    
            if not cat_id:
                cat = self.env['product.edesign.category'].create({
                    'name': cat_data['name'],
                    'default_code': cat_data['code']
                })
                cat_id = cat.id
            
            for sub_data in cat_data.get('subcategories', []):
                process_subcategory(sub_data, cat_id)
            
            for des_data in cat_data.get('designs', []):
                create_design(des_data, cat_id)
            
            for prod_data in cat_data.get('products', []):
                process_product(prod_data,cat_id)
            
            return cat_id
        
        def create_design(design_data, category_id = False):
            nonlocal created_designs
            design_id = design_data.get('id',False)
            if design_id:
                return design_id
            
            
            image_data = FolderScanner.get_files_data(design_data.get('image'))
            file_data = FolderScanner.get_files_data(design_data.get('file'))
            file_name = FolderScanner.get_file_name(design_data.get('file'))
            attachment_ids = []
            
            for att in design_data.get('attachments', []):
                att_data = FolderScanner.get_files_data(att.get('path'))
                if att_data:
                    attachment = self.env['ir.attachment'].create({
                        'name': att['name'],
                        'datas': att_data,
                        'res_model': 'product.edesign',
                    })
                    attachment_ids.append(attachment.id)
            
            design_id = self.env['product.edesign'].create({
                'name': design_data['name'],
                'default_code': design_data['code'],
                'category_id': category_id,
                'image': image_data,
                'file_name':file_name,
                'file_id': file_data,
                'attachment_ids': [(6, 0, attachment_ids)] if attachment_ids else False
            }).id
            created_designs += 1
            return design_id
        
        def process_subcategory(sub_data, category_id = False):
            sub_id = sub_data.get('id',False)
            if not sub_id:
                sub_id = self.env['product.edesign.category'].create({
                    'name': sub_data['name'],
                    'default_code': sub_data['code'],
                    'parent_id': category_id
                }).id
            
            for des_data in sub_data.get('designs', []):
                create_design(des_data, sub_id)
            
            for prod_data in sub_data.get('products', []):
                process_product(prod_data,sub_id)
            
            return sub_id
        
        def process_product(prod_data , category_id = False):
            product_id = prod_data.get('id',False)
            if not product_id:
                for des_data in prod_data.get('designs', []):
                    create_design(des_data, category_id)
                return None
            product = self.env['product.template'].browse(product_id)
            design_ids = []
            for des_data in prod_data.get('designs', []):
                des_id = create_design(des_data, category_id)
                design_ids.append(des_id)
            
            product.write({
                'design_ids': [Command.link(design_id) for design_id in design_ids]
            })
            
            return product_id
        
        for cat_data in preview_data.get('categories', []):
            process_category(cat_data)
        
        for prod_data in preview_data.get('products', []):
            process_product(prod_data)
        
        for des_data in preview_data.get('designs', []):
            create_design(des_data)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Import Successful',
                'message': f'{created_designs} designs loaded successfully',
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close'
                }
            }
        }
    
    def _create_attachments(self, files_data):
        attachment_ids = []
        
        for name, data in files_data['attachments']:
            try:
                attachment = self.env['ir.attachment'].create({
                    'name': name,
                    'datas': data,
                    'res_model': 'product.edesign',
                    'type': 'binary'
                })
                attachment_ids.append(attachment.id)
            except Exception:
                continue
        
        if files_data['image']:
            try:
                name, data = files_data['image']
                attachment = self.env['ir.attachment'].create({
                    'name': name,
                    'datas': data,
                    'res_model': 'product.edesign',
                    'type': 'binary'
                })
                attachment_ids.append(attachment.id)
            except Exception:
                pass
        
        if files_data['file']:
            try:
                name, data = files_data['file']
                attachment = self.env['ir.attachment'].create({
                    'name': name,
                    'datas': data,
                    'res_model': 'product.edesign',
                    'type': 'binary'
                })
                attachment_ids.append(attachment.id)
            except Exception:
                pass
        
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
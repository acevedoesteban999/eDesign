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
            counters['designs']['found'] += 1
            counters['subcategories']['new'] += 1 if not existing_des else 0
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
            counters['products']['found'] += 1
            
            if not existing_prod:
                result['error'] = True
                result['error_msg'] = _("Product not Found: %s",prod['code'])
                counters['products']['error'] += 1
            
            # counters['subcategories']['new'] += 1 if not existing_prod else 0
            
            for des in prod.get('designs', []):
                checked_des = check_design(des)
                if checked_des:
                    result['designs'].append(checked_des)
            return result
        
        def check_subcategory(sub, parent_cat_code=None):
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
                'parent_cat_code': parent_cat_code,
                'products': [],
                'designs': [],
            }
            counters['subcategories']['found'] += 1
            
            if existing_sub and not existing_sub.parent_id:
                result['error'] = True
                result['error_msg'] = _('Subcategory is not inside a valid. Dont have a category parent')
                counters['subcategories']['error'] += 1
                
            elif existing_sub and existing_sub.parent_id.default_code != parent_cat_code:
                result['error'] = True
                result['error_msg'] = _('Subcategory does not belong to this category (belongs to: %s)') % existing_sub.parent_id.name
        
            counters['subcategories']['new'] += 1 if not existing_sub and not result.get('error') else 0
            
            
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
                'id': existing_cat.id, 
                'subcategories': [],
                'products': [],
                'designs': [],
            }
            counters['categories']['found'] += 1
            
            if existing_cat and existing_cat.parent_id:
                result['error'] = True
                result['error_msg'] = _('Category is a subcategory in the system (belongs to: %s)') % existing_cat.parent_id.name
                counters['categories']['error'] += 1
                
            counters['categories']['new'] += 1 if not existing_cat and not result.get('error') else 0
                 
            for sub in cat.get('subcategories', []):
                checked_sub = check_subcategory(sub, cat['code'])
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
        
        counters = {
            'categories':{
                'color': 'primary',
                'title': _('Categories'),
                'color_text': 'light',
                
                'found': 0,
                'new': 0,
                'error': 0,
            },
            'subcategories':{
                'color': 'info',
                "title": _('Sub-Categories'),
                'color_text': 'light',
                
                'found': 0,
                'new': 0,
                'error': 0,
            },
            'products':{
                'color': 'warning',
                'title': 'Products',
                'color_text': 'dark',
                
                'found': 0,
                'new': 0,
                'error': 0,
            },
            'designs':{
                'color': 'success',
                'title': 'Designs',
                'color_text': 'light',
                
                'found': 0,
                'new': 0,
                'error': 0,
            },
        }
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
            'preview_data': {
                'preview_data':preview_data,
                'counters': counters,
                },
            'state': 'preview'
        })
        
        return self._reload_wizard()
    
    def action_confirm_import(self):
        self.ensure_one()
        
        preview_data = self.preview_data
        
        created_designs = 0
        
        def process_category(cat_data):
            if cat_data.get('error'):
                return
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
            
        
        def create_design(design_data, category_id = False):
            if design_data.get('error'):
                return
            nonlocal created_designs
            design_id = design_data.get('id',False)
            if design_id:
                return 
            
            
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
        
        def process_subcategory(sub_data, category_id = False):
            if sub_data.get('error'):
                return
        
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
            
        
        def process_product(prod_data , category_id = False):
            if prod_data.get('error'):
                return
            
            product_id = prod_data.get('id',False)
            if not product_id:
                for des_data in prod_data.get('designs', []):
                    create_design(des_data, category_id)
                return 
            product = self.env['product.template'].browse(product_id)
            design_ids = []
            for des_data in prod_data.get('designs', []):
                des_id = create_design(des_data, category_id)
                design_ids.append(des_id)
            
            product.write({
                'design_ids': [Command.link(design_id) for design_id in design_ids]
            })
            
        
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
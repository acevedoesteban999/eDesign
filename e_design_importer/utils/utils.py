import os
import re
from pathlib import Path
import base64

class FolderScanner:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.cat_pattern = re.compile(r'^(.*?)\s*\(CAT-(.+?)\)$')
        self.sub_pattern = re.compile(r'^(.*?)\s*\(SUB-(.+?)\)$')
        self.prod_pattern = re.compile(r'^(.*?)\s*\(PROD-(.+?)\)$')
        self.des_pattern = re.compile(r'^(.*?)\s*\((?:DES|DIS)-(.+?)\)$')
    
    def scan(self):
        return {
            'categories': self._scan_categories(self.root_path),
            'designs': self._scan_designs(self.root_path),
            'products': self._scan_designs(self.root_path),
        }
    
    def _scan_categories(self, path):
        categories = []
        
        for item in path.iterdir():
            if not item.is_dir():
                continue
            
            cat_match = self.cat_pattern.match(item.name)
            if cat_match:
                category = self._process_category(item, cat_match)
                categories.append(category)
        
        return categories
    
    def _process_category(self, cat_path, cat_match):
        return {
            'name': cat_match.group(1).strip(),
            'code': cat_match.group(2).strip(),
            'path': str(cat_path),
            'subcategories': self._scan_subcategories(cat_path),
            'products': self._scan_products(cat_path),
            'designs': self._scan_designs(cat_path)
        }
    
    def _scan_subcategories(self, path):
        subcategories = []
        
        for item in path.iterdir():
            if not item.is_dir():
                continue
            
            sub_match = self.sub_pattern.match(item.name)
            if sub_match:
                subcategory = {
                    'name': sub_match.group(1).strip(),
                    'code': sub_match.group(2).strip(),
                    'path': str(item),
                    'products': self._scan_products(item),
                    'designs': self._scan_designs(item)
                }
                subcategories.append(subcategory)
        
        return subcategories
    
    def _scan_products(self, path):
        products = []
        
        for item in path.iterdir():
            if not item.is_dir():
                continue
            
            prod_match = self.prod_pattern.match(item.name)
            if prod_match:
                product = {
                    'name': prod_match.group(1).strip(),
                    'code': prod_match.group(2).strip(),
                    'path': str(item),
                    'designs': self._scan_designs(item)
                }
                products.append(product)
        
        return products
    
    
    def _scan_designs(self, path):
        designs = []
        
        for item in path.iterdir():
            if not item.is_dir():
                continue
            
            des_match = self.des_pattern.match(item.name)
            if des_match:
                design = self._process_design(item, des_match)
                designs.append(design)
        
        return designs
    
    def _process_design(self, des_path, des_match):
        design = {
            'name': des_match.group(1).strip(),
            'code': des_match.group(2).strip(),
            'path': str(des_path),
            'image': None,
            'file': None,
            'attachments': []
        }
        
        for item in des_path.iterdir():
            if item.is_file():
                if item.name.lower().startswith('image.'):
                    design['image'] = str(item)
                elif item.name.lower().startswith('file.'):
                    design['file'] = str(item)
            
            elif item.is_dir() and item.name.lower() == 'attachments':
                design['attachments'] = self._scan_attachments(item)
        
        return design
    
    def _scan_attachments(self, attachments_path):
        attachments = []
        
        for item in attachments_path.iterdir():
            if not item.is_file():
                continue
            
            size_mb = item.stat().st_size / (1024 * 1024)
            if size_mb <= 100:
                attachments.append({
                    'name': item.name,
                    'path': str(item),
                })
        
        return attachments
    
    @staticmethod
    def get_files_data(path):
        if not path or not os.path.exists(path):
            return None
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
        
    @staticmethod
    def get_file_name(path):
        if not path or not os.path.exists(path):
            return None
        return os.path.basename(path)
        
import os
import re
from pathlib import Path
import base64

class FolderScanner:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.marker_pattern = re.compile(r'^(.*?)\s*\((CAT|SUB|PROD|DES|DIS)-(.+?)\)\s*(.*?)$')
    
    def scan(self):
        return {
            'categories': self._scan_categories(self.root_path),
            'designs': self._scan_designs(self.root_path),
            'products': self._scan_designs(self.root_path),
        }
    
    def _extract_name_and_code(self, match):
        before = match.group(1).strip()
        code = match.group(3).strip()
        after = match.group(4).strip()
        
        parts = [p for p in [before, after] if p]
        name = ' '.join(parts)
        
        return name, code
    
    def _scan_categories(self, path):
        categories = []
        
        for item in path.iterdir():
            if not item.is_dir():
                continue
            
            match = self.marker_pattern.match(item.name)
            if match and match.group(2) == 'CAT':
                category = self._process_category(item, match)
                categories.append(category)
            elif not self._has_special_marker(item.name):
                flattened = self._scan_categories(item)
                categories.extend(flattened)
        
        return categories
    
    def _scan_subcategories(self, path):
        subcategories = []
        
        for item in path.iterdir():
            if not item.is_dir():
                continue
            
            match = self.marker_pattern.match(item.name)
            if match and match.group(2) == 'SUB': 
                name, code = self._extract_name_and_code(match)
                subcategory = {
                    'name': name,
                    'code': code,
                    'path': str(item),
                    'products': self._scan_products(item),
                    'designs': self._scan_designs(item)
                }
                subcategories.append(subcategory)
            elif not self._has_special_marker(item.name):
                flattened = self._scan_subcategories(item)
                subcategories.extend(flattened)
        
        return subcategories
    
    def _scan_products(self, path):
        products = []
        
        for item in path.iterdir():
            if not item.is_dir():
                continue
            
            match = self.marker_pattern.match(item.name)
            if match and match.group(2) == 'PROD': 
                name, code = self._extract_name_and_code(match)
                product = {
                    'name': name,
                    'code': code,
                    'path': str(item),
                    'designs': self._scan_designs(item)
                }
                products.append(product)
            elif not self._has_special_marker(item.name):
                flattened = self._scan_products(item)
                products.extend(flattened)
        
        return products
    
    def _scan_designs(self, path):
        designs = []
        
        for item in path.iterdir():
            if not item.is_dir():
                continue
            
            match = self.marker_pattern.match(item.name)
            if match and match.group(2) in ('DES'):
                design = self._process_design(item, match)
                designs.append(design)
            elif not self._has_special_marker(item.name):
                flattened = self._scan_designs(item)
                designs.extend(flattened)
        
        return designs
    
    def _has_special_marker(self, folder_name):
        match = self.marker_pattern.match(folder_name)
        return match is not None and match.group(2) in ('CAT', 'SUB', 'PROD', 'DES')
    
    def _process_category(self, cat_path, match):
        name, code = self._extract_name_and_code(match)
        return {
            'name': name,
            'code': code,
            'path': str(cat_path),
            'subcategories': self._scan_subcategories(cat_path),
            'products': self._scan_products(cat_path),
            'designs': self._scan_designs(cat_path)
        }
    
    def _process_design(self, des_path, match):
        name, code = self._extract_name_and_code(match)
        design = {
            'name': name,
            'code': code,
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
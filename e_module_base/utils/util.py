import os
from pathlib import Path

from odoo.modules.module import load_manifest

def _os_path_dir(path,count):
    if count > 0:
        return os.path.dirname(_os_path_dir(path,count-1))
    return path

def scan_addon_path(addon_path):
   valid_modules = []   
   try:
       for entry in os.scandir(addon_path):
           if not entry.is_dir() or entry.name.startswith('.') or entry.name.startswith('_'):
               continue
           
           module_path = entry.path
           try:
               manifest = load_manifest(entry.name, mod_path=module_path)
               
               if manifest:
                   valid_modules.append({
                       'name': entry.name,
                       'path': module_path,
                       'version': manifest.get('version', 'unknown'),
                       'depends': manifest.get('depends', []),
                   })
                   
           except Exception as e:
               continue
               
   except Exception as e:
        pass
   return valid_modules
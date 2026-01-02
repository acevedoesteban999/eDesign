# -*- coding: utf-8 -*-
# Copyright 2025 
# License LGPL-3

import os
import io
import shutil
import datetime
import zipfile
import logging

_logger = logging.getLogger(__name__)

def make_backup(local_path, module_name, version):
    try:
        base_module_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        backup_base = os.path.join(base_module_path, '.backups', module_name)
        os.makedirs(backup_base, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
        zip_filename = f"v{version}-{timestamp}.zip"
        zip_path = os.path.join(backup_base, zip_filename)
        
        if os.path.exists(local_path) and os.path.isdir(local_path):
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(local_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(local_path))
                        zipf.write(file_path, arcname)
            
            _logger.info("Backup ZIP created: %s", zip_path)
            return zip_path
        else:
            _logger.warning("Module path doesn't exist, backup skipped: %s", local_path)
            return None
            
    except Exception as e:
        _logger.error("Failed to create backup ZIP: %s", str(e))
        raise

def remove_backup(backup_path):
    try:
        if backup_path and os.path.exists(backup_path) and os.path.isfile(backup_path):
            os.remove(backup_path)
            _logger.info("Backup ZIP removed: %s", backup_path)
        elif backup_path and os.path.exists(backup_path):
            shutil.rmtree(backup_path)
    except Exception as e:
        _logger.error("Failed to remove backup %s: %s", backup_path, str(e))


def copy_zip_by_path(zip_path:str , prefix:str, local_path:str):
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        return copy_zip(zip_file,prefix,local_path)
    
def copy_zip(zip_file:zipfile.ZipFile , local_path:str):
    if local_path and os.path.exists(local_path):
        shutil.rmtree(local_path)
    count_files = 0
    for zip_info in zip_file.infolist():
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with zip_file.open(zip_info) as source, open(local_path, 'wb') as target:
            shutil.copyfileobj(source, target)
        count_files += 1 
    return count_files

def restore_backup(backup_path, local_path, _remove_backup = False):
    try:
        if backup_path and os.path.exists(backup_path) and os.path.isfile(backup_path):
            copy_zip_by_path(backup_path,'',local_path)
            _logger.info("Restored backup ZIP from %s to %s", backup_path, local_path)
            if _remove_backup:
                remove_backup(backup_path)
        else:
            _logger.error("Backup ZIP not found: %s", backup_path)
            raise Exception("Backup ZP not found: %s" % backup_path)
    except Exception as e:
        _logger.error("Failed to restore backup ZIP: %s", str(e))
        raise
    
def get_zip_by_prefix(zip_file:zipfile.ZipFile , prefix:str):
    filtered_zip_buffer = io.BytesIO()
    with zipfile.ZipFile(filtered_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as filtered_zip:
        for zip_info in zip_file.infolist():
            if zip_info.is_dir():
                continue
            if zip_info.filename.startswith(prefix):
                relative_path = zip_info.filename[len(prefix):]
                file_content = zip_file.read(zip_info.filename)
                filtered_zip.writestr(relative_path, file_content)
    
    filtered_zip_buffer.seek(0)
    zip_for_extraction = zipfile.ZipFile(filtered_zip_buffer, 'r')
    return zip_for_extraction
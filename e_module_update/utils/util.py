import os
import shutil
import datetime

def process_zip(zip_file,prefix,local_path):
    count_files = 0
    for zip_info in zip_file.infolist():
        if (prefix and zip_info.filename.startswith(prefix)) and not zip_info.is_dir():
            relative_path = zip_info.filename[len(prefix):]
            if relative_path: 
                target_path = os.path.join(local_path, relative_path)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                
                with zip_file.open(zip_info) as source, open(target_path, 'wb') as target:
                    shutil.copyfileobj(source, target)
                count_files += 1 
    return count_files

def make_backup(local_path,module_name):
    backup_path = local_path + '.backup_'+ module_name + datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    shutil.move(local_path, backup_path)
    os.makedirs(local_path, exist_ok=True)
    return backup_path

def remove_backup(path):
    if os.path.exists(path):    
        shutil.rmtree(path)

def restore_backup(backup_path,local_path):
    shutil.rmtree(local_path)
    shutil.move(backup_path, local_path)
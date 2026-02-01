# -*- coding: utf-8 -*-
import io
import os
import polib
from odoo.tools.translate import trans_export
from datetime import datetime

def get_pots_from_export(modules_name:list,cr):
    return [ get_pot_from_export(module, cr)for module in modules_name ] 

def get_pot_from_export(module_name,cr):
    with io.BytesIO() as buf:
        trans_export(False, [module_name], buf, 'po', cr)
        buf.seek(0)
        content = buf.read().decode('utf-8')
        return polib.pofile(content)

def get_po_from_file(local_path,lang):
    pot_path = os.path.join(local_path, 'i18n', f'{lang}.po')
    if not os.path.isfile(pot_path):
        return None
    return polib.pofile(pot_path)

def get_pot_from_file(local_path,module_name):
    pot_path = os.path.join(local_path, 'i18n', f'{module_name}.pot')
    if not os.path.isfile(pot_path):
        return None
    return polib.pofile(pot_path)


def compare_pot_files(local_path,module_name,cr,pot_file_cached=False):
    
    if not pot_file_cached:
        file_pot = get_pot_from_export(module_name,cr)
    else:
        file_pot = pot_file_cached
        
    if not file_pot:
        return False
    
    exported_pot = get_pot_from_file(local_path, module_name)
        
    exported_keys = {entry.msgid for entry in exported_pot if entry.msgid}
    file_keys = {entry.msgid for entry in file_pot if entry.msgid}

    missing_in_file = exported_keys - file_keys
    extra_in_file = file_keys - exported_keys
    common_keys = exported_keys & file_keys

    return common_keys, missing_in_file, extra_in_file


def save_pot_file(local_path, module_name, pot_data):
    i18n_path = os.path.join(local_path, 'i18n')
    os.makedirs(i18n_path, exist_ok=True)
    
    pot_path = os.path.join(i18n_path, f'{module_name}.pot')
    
    po_file = polib.POFile()
    po_file.metadata = {
        'Project-Id-Version': f'{module_name} 1.0',
        'Report-Msgid-Bugs-To': '',
        'POT-Creation-Date': datetime.now().strftime('%Y-%m-%d %H:%M%z'),
        'PO-Revision-Date': '',
        'Last-Translator': '',
        'Language-Team': '',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=UTF-8',
        'Content-Transfer-Encoding': '8bit',
        'Plural-Forms': 'nplurals=2; plural=(n != 1);',
    }
    
    for msgid in pot_data.values():
        if msgid: 
            entry = polib.POEntry(msgid=msgid)
            po_file.append(entry)
    
    po_file.save(pot_path)
    return pot_path


def save_po_file(local_path, lang_code, pot_data, translations):
    i18n_path = os.path.join(local_path, 'i18n')
    os.makedirs(i18n_path, exist_ok=True)
    
    po_path = os.path.join(i18n_path, f'{lang_code}.po')
    
    valid_translations = {
        k: v for k, v in translations.items() 
        if v and str(v).strip()
    }
    
    if not valid_translations:
        if os.path.exists(po_path):
            os.remove(po_path)
        return None
    
    from .translate import generate_po_content
    
    pot_metadata = None
    pot_path = os.path.join(i18n_path, f'{os.path.basename(local_path)}.pot')
    if os.path.exists(pot_path):
        try:
            pot_file = polib.pofile(pot_path)
            pot_metadata = pot_file.metadata
        except:
            pass
    
    content = generate_po_content(pot_data, valid_translations, lang_code, pot_metadata)
    
    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return po_path
    
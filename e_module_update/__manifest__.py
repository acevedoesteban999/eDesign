# -*- coding: utf-8 -*-
{
    'name': 'eModuleUpdate',
    'version': '18.0.0.0',
    'summary': """ Can Update module repository from git """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', ],
    "data": [
        "security/ir.model.access.csv",
        "views/ir_module_e_update.xml",
        "views/ir_module_e_update_git.xml",
        "views/ir_module_e_update_manual.xml",
        "views/menu.xml",
    ],
    
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

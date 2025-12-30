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
        "views/ir_module_e_updater.xml",
        "wizard/module_update_manual_wizard.xml",
        "views/menu.xml",
    ],
    
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

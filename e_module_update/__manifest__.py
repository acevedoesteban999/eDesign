# -*- coding: utf-8 -*-
{
    'name': 'eModuleUpdate',
    'version': '18.0.0.0',
    'summary': """ Can Update module repository """,
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eAddons/blob/18.0/e_module_update',
    'category': '',
    'depends': ['base', 'web','e_module_base'],
    "data": [
        "security/ir.model.access.csv",
        "views/ir_module_e_update.xml",
        "views/ir_module_e_update_git_remote.xml",
        "views/ir_module_e_update_manual.xml",
        "views/ir_module_e_update_backups.xml",
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "e_module_update/static/src/view/list/list_arch_parser.js",
            "e_module_update/static/src/view/list/list_renderer.xml",
            "e_module_update/static/src/view/list/list_renderer.js",
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

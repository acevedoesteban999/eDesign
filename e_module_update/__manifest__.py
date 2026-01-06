# -*- coding: utf-8 -*-
{
    'name': 'eModuleUpdate',
    'version': '18.0.0.0',
    'summary': """ Can Update module repository from git """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'web'],
    "data": [
        "security/ir.model.access.csv",
        "views/ir_module_e_update.xml",
        "views/ir_module_e_update_git.xml",
        "views/ir_module_e_update_manual.xml",
        "wizard/restart_server.xml",
        
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "e_module_update/static/src/view/list/list_arch_parser.js",
            "e_module_update/static/src/view/list/list_renderer.xml",
            "e_module_update/static/src/view/list/list_renderer.js",
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

# -*- coding: utf-8 -*-
{
    'name': 'eModuleBase',
    'version': '18.0.0.0',
    'summary': """ Base Module for eModules """,
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eAddons/blob/18.0/e_module_base',
    'category': '',
    'depends': ['base', 'web'],
    "data": [
        "views/ir_module_e_base.xml",
    ],
    # "assets": {
    #     "web.assets_backend": [
    #         "e_module_update/static/src/view/list/list_arch_parser.js",
    #         "e_module_update/static/src/view/list/list_renderer.xml",
    #         "e_module_update/static/src/view/list/list_renderer.js",
    #     ],
    # },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

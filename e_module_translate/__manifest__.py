# -*- coding: utf-8 -*-
{
    'name': 'eModuleTranslate',
    'version': '18.0.0.1.0',
    'summary': """ Check and trnslate POT and PO extension for modules """,
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eAddons/blob/18.0/e_module_translate',
    'category': '',
    'depends': ['base', 'web' , 'e_module_base'],
    'data': [
        'security/ir.model.access.csv',
        'views/ir_module_e_translate.xml',
        "wizards/ir_module_e_translate_autotranslate_wizard.xml",
        "wizards/addon_modules_wizard.xml",
        
        "views/menu.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'e_module_translate/static/src/components/**/*'
        ],
    },
    'external_dependencies': {
        'python': [
            'googletrans',
        ]
    },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

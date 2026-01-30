# -*- coding: utf-8 -*-
{
    'name': 'eModuleTranslate',
    'version': '18.0.0.0',
    'summary': """ Check and trnslate POT and PO extension for modules """,
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eAddons/blob/18.0/e_module_translate',
    'category': '',
    'depends': ['base', 'web' , 'e_module_base'],
    'data': [
        'security/ir.model.access.csv',
        'views/ir_module_e_translate.xml',
        "views/menu.xml"
    ],
    'assets': {
        'web.assets_backend': [
            'e_module_translate/static/src/components/**/*'
        ],
    },
    'external_dependencies': {
        'python': [
            'google-cloud-translate',
        ]
    },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

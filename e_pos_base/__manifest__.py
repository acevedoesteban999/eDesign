# -*- coding: utf-8 -*-
{
    'name': 'eBasePos',
    'version': '18.0.0.0.0',
    'summary': "Base ePos",
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eAddons/blob/18.0/e_pos_base',
    'category': 'Customizations',
    'depends': ['web','point_of_sale'],
    'data': [],
    'assets': {
        'point_of_sale._assets_pos': [
            'e_pos_base/static/src/components/**/*',
            'e_pos_base/static/src/scss/styles.scss',
        ],
    },
    
    'images': [
        'static/description/banner.png',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

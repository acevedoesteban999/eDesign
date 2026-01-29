# -*- coding: utf-8 -*-
{
    'name': 'eAccountDesign',
    'version': '18.0.3.0.0',
    'summary': """ Add design to account's lines """,
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eAddons/blob/18.0/e_design_account',
    'category': 'Invoicing',
    'depends': ['base','account','e_design','e_design_sale'],
    "data": [
        "views/account_move.xml",
    ],
    'images': [
        'static/description/banner.png',
    ],
    'application': False,
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}

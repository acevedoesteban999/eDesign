# -*- coding: utf-8 -*-
{
    'name': 'eDesignSale',
    'version': '18.0.3.0.0',
    'summary': """ Add design to sale's lines """,
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eAddons/blob/18.0/e_design_sale',
    'category': 'Sales',
    'depends': ['sale','e_design'],
    "data": [
        "views/sale_order.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "e_design_sale/static/src/components/**/*",
        ],
    },
    'images': [
        'static/description/banner.png',
    ],
    'application': False,
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}

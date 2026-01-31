# -*- coding: utf-8 -*-
{
    'name': 'eMtoDinamic',
    'version': '18.0.1.0.0',
    'summary': """ Create Dinamic Products for Dinamic Bill of Material """,
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eAddons/blob/18.0/e_mto_dinamic',
    'category': '',
    'depends': ['base','web','product' , 'sale_stock' , 'mrp','e_mto_base'],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template.xml",
        "views/sale_order.xml"
    ],
    'assets': {
        'web.assets_backend': [
            'e_mto_dinamic/static/src/componets/**/*'
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

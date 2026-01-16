# -*- coding: utf-8 -*-
{
    'name': 'eProductGeneric',
    'version': '18.0.0.0',
    'summary': """ Create Generic Products for Dinamic Bill of Material """,
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eDesign/blob/18.0/e_porduct_generic',
    'category': '',
    'depends': ['base','web','product' , 'sale_stock' , 'sale_mrp'],
    'data': [
        "views/product_template.xml",
        "views/sale_order.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'e_product_generic/static/src/componets/**/*'
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

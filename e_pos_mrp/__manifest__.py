# -*- coding: utf-8 -*-
{
    'name': 'ePosMrp',
    'version': '18.0.0.1',
    'summary': "Integration POS with MRP",
    'description':"It allows you to create manufacturing orders for Point of Sale",
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eDesign/blob/master/e_pos_mrp',
    'category': 'Customizations',
    'depends': ['base', 'pos_mrp'],
    'data': [
        "views/pos_order.xml",
        "views/product_template.xml",
        "views/mrp_production.xml",
    ],
    'images': [
        'static/description/banner.png',
    ],
    'application': False,
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}

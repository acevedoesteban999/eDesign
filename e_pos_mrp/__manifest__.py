# -*- coding: utf-8 -*-
{
    'name': 'e_pos_mrp',
    'version': '18.0.0.1',
    'summary': "Integration POS with MRP",
    'description':"It allows you to create manufacturing orders for Point of Sale",
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eDesign',
    'category': 'Customizations',
    'depends': ['base', 'pos_mrp'],
    'data': [
        "views/pos_order.xml",
        "views/product_template.xml",
    ],
    
    'application': False,
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}

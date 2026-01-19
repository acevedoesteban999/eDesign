# -*- coding: utf-8 -*-
{
    'name': 'ePosMrp',
    'version': '18.0.1.0',
    'summary': "Integration POS with MRP",
    'description':"It allows you to create manufacturing orders for Point of Sale",
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eAddons/blob/18.0/e_pos_mrp',
    'category': 'Customizations',
    'depends': ['base' , 'point_of_sale', 'mrp'],
    'data': [
        "views/pos_order.xml",
        "views/product_template.xml",
        "views/res_config.xml",
        "views/mrp_production.xml",
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'e_pos_mrp/static/src/components/**/*',
            'e_pos_mrp/static/src/scss/styles.scss',
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

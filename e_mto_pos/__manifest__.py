# -*- coding: utf-8 -*-
{
    'name': 'eMtoPos',
    'version': '18.0.0.1.1',
    'summary': "Integration POS with MRP",
    'description':"It allows you to create manufacturing orders for Point of Sale",
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eAddons/blob/18.0/e_mto_pos',
    'category': 'Customizations',
    'depends': ['base' , 'pos_mrp','e_mto_base'],
    'data': [
        "security/ir.model.access.csv",
        
        "views/pos_order.xml",
        "views/product_template.xml",
        "views/res_config.xml",
        "views/mrp_production.xml",
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'e_mto_pos/static/src/components/**/*',
            'e_mto_pos/static/src/scss/styles.scss',
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

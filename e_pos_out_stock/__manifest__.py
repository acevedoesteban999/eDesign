# -*- coding: utf-8 -*-
{
    'name': 'ePosOutStock',
    'version': '18.0.0.0',
    'summary': "Hide out of stock POS products",
    'description':"It allows hide products out of stock from pos. Can inactive from specific products or pos categories",
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eDesign/blob/18.0/e_pos_out_stock',
    'category': 'Customizations',
    'depends': ['base',"point_of_sale"],
    'data': [
        'security/groups.xml',
        
        "views/pos_category.xml",
        "views/product_template.xml",
        "views/res_config.xml",
    ],
    'images': [
        'static/description/banner.png',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'e_pos_out_stock/static/src/js/*.js',
            'e_pos_out_stock/static/src/components/*/**',
        ],
    },
    
    'application': False,
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}

# -*- coding: utf-8 -*-
{
    'name': 'eDesignPos',
    'version': '18.0.0.0',
    'summary': "Integration POS with eDesign",
    'description':"It allows integrate eDesign with Point of Sale",
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eDesign/blob/18.0/e_design_pos',
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
            'e_design_pos/static/src/js/pos_store.js',
            'e_design_pos/static/src/js/pos_screen.js',
        ],
    },
    
    'application': False,
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}

# -*- coding: utf-8 -*-
{
    'name': 'ePosMrp',
    'version': '18.0.1.0.0',
    'summary': "Create MRP orders in POS",
    'description':"It allows you to create manufacturing orders for Point of Sale",
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eAddons/blob/18.0/e_pos_mrp',
    'category': 'Customizations',
    'depends': ['base' , 'pos_mrp'],
    "data": [
        "security/ir.model.access.csv",
        "wizards/creata_order_wizard.xml",
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'e_pos_mrp/static/src/components/**/*',
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

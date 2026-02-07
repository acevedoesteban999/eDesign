# -*- coding: utf-8 -*-
{
    'name': 'eDesignPos',
    'version': '18.0.3.0.2',
    'summary': """Integration POS-MRP with eDesign""",
    'description':"""
                    It allows you to view the designs of the product 
                    to be manufactured in the manufacturing orders.
                """,
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eAddons/blob/18.0/e_design_mrp',
    'category': 'Customizations',
    'depends': ['e_design','point_of_sale'],
    "data": [
        "views/pos_order.xml",
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            "e_design/static/src/components/edesign_selection/*",
            'e_design_pos/static/src/components/**/*',
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

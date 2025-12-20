# -*- coding: utf-8 -*-
{
    'name': 'ePosMrpDesign',
    'version': '19.0.0',
    'summary': """Integration POS-MRP with eDesign""",
    'description':"""
                    It allows you to view the designs of the product 
                    to be manufactured in the manufacturing orders.
                """,
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eDesign/blob/19.0/e_pos_mrp_design',
    'category': 'Customizations',
    'depends': ['sale_mrp','e_pos_mrp','e_design'],
    "data": [
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

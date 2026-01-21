# -*- coding: utf-8 -*-
{
    'name': 'eDesignMrp',
    'version': '18.0.1.0.0',
    'summary': """Integration MRP with eDesign""",
    'description':"""
                    It allows you to view the designs of the product 
                    to be manufactured in the manufacturing orders.
                """,
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eAddons/blob/18.0/e_design_mrp',
    'category': 'Customizations',
    'depends': ['mrp','e_design'],
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

# -*- coding: utf-8 -*-
{
    'name': 'edesignBundle',
    'version': '19.0.0',
    'summary': """ eDesign Bundle for all eDesign addons""",
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eDesign/tree/19.0',
    'category': '',
    'depends': ['base','e_design','e_pos_mrp','e_pos_mrp_design','e_website_design','e_sale_design','e_account_design' ],
    'images': [
        'static/description/banner.png',
    ],
    "data": [
        "views/base_views.xml"
    ],
    'application': False,
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}

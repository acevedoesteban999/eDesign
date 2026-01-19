# -*- coding: utf-8 -*-
{
    'name': 'eDesignBundle',
    'version': '18.1.0',
    'summary': """ eDesign Bundle for all eDesign addons""",
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eAddons',
    'category': '',
    'depends': ['base','e_design','e_pos_mrp','e_design_pos_mrp','e_design_website','e_design_sale','e_design_account' ],
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

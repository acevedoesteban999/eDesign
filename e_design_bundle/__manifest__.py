# -*- coding: utf-8 -*-
{
    'name': 'eDesignBundle',
    'version': '18.1.0',
    'summary': "Complete bundle for all eDesign addons",
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eAddons',
    'category': 'Customizations',
    'depends': [
        'e_design',
        'e_pos_mrp',
        'e_design_mrp_pos',
        'e_design_pos',
        'e_design_website',
        'e_design_website_tv_catalog',
        'e_design_sale',
        'e_design_account',
    ],
    'images': [
        'static/description/banner.png',
    ],
    "data": [
        "views/base_views.xml"
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

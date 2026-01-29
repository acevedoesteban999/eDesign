# -*- coding: utf-8 -*-
{
    'name': 'eWebsiteDesign',
    'version': '18.0.3.0.0',
    'summary': "Integration eDesign with Website",
    'description':"""
                    It allows you to view the design catalog from the website.
                """,
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eAddons/blob/18.0/e_design_website_tv_catalog',
    'category': 'Customizations',
    'depends': ['e_design_website'],
    'data': [
        "views/pages/tv_catalog.xml",
        
    ],
    "assets": {
        "web.assets_frontend": [
            "e_design_website_tv_catalog/static/src/scss/*.scss",
            "e_design_website_tv_catalog/static/src/js/*js",
        ],
    },
    'images': [
        'static/description/banner.png',
    ],
    
    'post_init_hook': '_install_tv_catalog_menu_and_page',
    'uninstall_hook': '_uninstall_tv_catalog_menu_and_page',
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

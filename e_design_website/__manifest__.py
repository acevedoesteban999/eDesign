# -*- coding: utf-8 -*-
{
    'name': 'eWebsiteDesign',
    'version': '18.0.1.0',
    'summary': "Integration eDesign with Website",
    'description':"""
                    It allows you to view the design catalog from the website.
                """,
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eAddons/blob/18.0/e_design_website',
    'category': 'Customizations',
    'depends': ['base','e_design','website'],
    'data': [
        "views/components.xml",
        "views/templates.xml",
        "views/product_edesign.xml",
        "views/product_edesign_category.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "e_design_website/static/src/components/public/**/*",
            "e_design_website/static/src/scss/*.scss",
            "e_design_website/static/src/js/*js",
        ],
    },
    'images': [
        'static/description/banner.png',
    ],
    'post_init_hook': '_install_designs_menu_and_page',
    'uninstall_hook': '_uninstall_designs_menu_and_page',
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

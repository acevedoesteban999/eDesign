# -*- coding: utf-8 -*-
{
    'name': 'eWebsiteDesign',
    'version': '19.0.0',
    'summary': "Integration eDesign with Website",
    'description':"""
                    It allows you to view the design catalog from the website.
                """,
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eDesign/blob/19.0/e_website_design',
    'category': 'Customizations',
    'depends': ['base','e_design','website'],
    'data': [
        "views/components.xml",
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "e_website_design/static/src/components/public/**/*",
            "e_website_design/static/src/scss/*.scss",
            "e_website_design/static/src/js/*js",
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

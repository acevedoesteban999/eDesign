# -*- coding: utf-8 -*-
{
    'name': 'e_website_design',
    'version': '18.0.0.1',
    'summary': """Integration Website with EDesign""",
    'author': 'acevedoesteban999@gmail.com',
    'website': '',
    'category': '',
    'depends': ['base','e_design','website'],
    'data': [
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "e_design/static/src/components/**/**/*",
        ],
        "web.assets_frontend": [
            "e_design/static/src/scss/public_design.scss",
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}

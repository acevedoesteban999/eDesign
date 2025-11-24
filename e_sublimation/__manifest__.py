# -*- coding: utf-8 -*-
{
    'name': 'E-Sublimation',
    'version': '1.1.0',
    'summary': """ E-Sublimation Summary """,
    'author': 'acevedoesteban999@gmail.com',
    'website': '',
    'category': '',
    'depends': [
        'base', 
        'product',
        'stock',
    ],
    "data": [
        "data/data.xml",
        "security/ir.model.access.csv",
        "views/product_design_views.xml",
        "views/product_template.xml",
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "e_sublimation/static/src/components/**/*",
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

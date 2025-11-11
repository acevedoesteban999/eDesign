# -*- coding: utf-8 -*-
{
    'name': 'E-Sublimation',
    'version': '1.1.0',
    'summary': """ E-Sublimation Summary """,
    'author': 'acevedoesteban999@gmail.com',
    'website': '',
    'category': '',
    'depends': ['base', 'product','stock'],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template.xml",
        "wizard/sublimation_attachment_wizard.xml",
        "wizard/sublimation_wizard.xml",
        "views/e_sublimation_category_views.xml",
        
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "e_sublimation/static/src/js/*.js",
        ],
    },
    
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

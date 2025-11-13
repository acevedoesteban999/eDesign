# -*- coding: utf-8 -*-
{
    'name': 'E-Sublimation',
    'version': '1.1.0',
    'summary': """ E-Sublimation Summary """,
    'author': 'acevedoesteban999@gmail.com',
    'website': '',
    'category': '',
    'depends': ['base', 'product','stock','website'],
    "data": [
        "security/ir.model.access.csv",
        "views/category_views.xml",
        "views/product_template.xml",
        "views/templates.xml",
        "wizard/sublimation_attachment_wizard.xml",
        "wizard/sublimation_wizard.xml",
        
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "e_sublimation/static/src/js/*",
            "e_sublimation/static/src/widget/**/*",
        ],
        "web.assets_frontend": [
            "e_sublimation/static/src/components/**/*",
        ],
    },
    
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

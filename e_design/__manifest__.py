# -*- coding: utf-8 -*-
{
    'name': 'E-Design',
    'version': '1.1.0',
    'summary': "Add Design to Products",
    'description':"""
                    It allows you to add designs to products, 
                    creating non-real variants to select as an additional attribute.
                """,
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eDesign',
    'category': 'Customizations',
    'depends': [
        'base', 
        'product',
        'stock',
    ],
    "data": [
        "data/data.xml",
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/product_design_category.xml",
        "views/product_design.xml",
        "views/product_template.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "e_design/static/src/components/**/**/*",
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

# -*- coding: utf-8 -*-
{
    'name': 'eDesign',
    'version': '18.0.4.2',
    'summary': "Add Design to Products",
    'description':"""
                    It allows you to add designs to products, 
                    creating non-real variants to select as an additional attribute.
                """,
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eDesign/blob/18.0/e_design',
    'category': 'Customizations',
    'images': [
        'static/description/banner.png',
    ],
    'depends': [
        'base', 
        'product',
        'stock',
    ],
    "data": [
        "security/e_design.xml",
        
        "data/data.xml",
        "security/ir.model.access.csv",
        "views/product_design_category.xml",
        "views/product_design.xml",
        "views/product_template.xml",
        
        "widget/product_design_attach_widget.xml",
        "widget/product_design_unlink_widge.xml",
        
        "views/menu.xml",
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

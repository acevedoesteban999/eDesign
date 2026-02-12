# -*- coding: utf-8 -*-
{
    'name': 'eVideoContent',
    'version': '18.0.0.0.1',
    'summary': "Video as File ",
    'description':"""
                    
                """,
    'author': 'acevedoesteban999@gmail.com',
    'website': 'https://github.com/acevedoesteban999/eAddons/blob/18.0/e_video_content',
    'category': 'Customizations',
    'depends': ['base'],
    'data': [
        "security/ir.model.access.csv",
        "views/video_content_views.xml", 
    ],
    "assets": {
        "web.assets_backend":[
            "e_video_content/static/src/components/**/*",
        ]
    },
    'images': [
        'static/description/banner.png',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

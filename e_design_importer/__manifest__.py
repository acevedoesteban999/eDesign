{
    'name': 'eDesignImporter',
    'version': '18.0.0.0.0',
    'category': '',
    'summary': '',
    'depends': ['e_design', 'web'],
    "data": [
        "security/ir.model.access.csv",
        
        "views/menu_views.xml",
        "wizards/import_design_wizard.xml",
    ],
    'assets': {
        'web.assets_backend': [
            '/e_design_importer/static/src/components/*/**',
        ],
    },
    'installable': True,
    'application': False,
}
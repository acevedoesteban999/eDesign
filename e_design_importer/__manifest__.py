{
    'name': 'eDesignImporter',
    'version': '18.0.1.1.0',
    'category': '',
    'summary': '',
    'depends': ['e_design', 'web', 'report_xlsx'],
    "data": [
        "security/ir.model.access.csv",
        
        "views/product_report_menus.xml",
        
        "views/menu_views.xml",
        "wizards/import_design_wizard.xml",
    ],
    'assets': {
        'web.assets_backend': [
            '/e_design_importer/static/src/components/*/**',
        ],
    },
    'installable': True,
    'application': True,
}
from odoo import http, _
from odoo.http import request
import json

class TvCatalog(http.Controller):
    
    @http.route('/tv/catalog', type='http', auth='user', website=True)
    def tv_catalog(self):
        return request.render('e_design_website_tv_catalog.TVCatalog', {
            'title': _("Catalog"),
            'config': json.dumps({
                'autoplay': 5000,
                'scroll_speed': 1.0,
                'refresh_interval': 3600000,
                'maxItemsPerSlide': 8,
            })
        })

    @http.route('/tv/catalog/data', type='json', auth='user')
    def tv_catalog_data(self):
        groups = []
        Category = request.env['product.edesign.category']
        Product = request.env['product.template']
        Design = request.env['product.edesign']

        parent_categories = Category.search([
            ('is_published', '=', True),
            ('parent_id', '=', False),
        ])

        for category in parent_categories:
            all_designs = []
            
            direct_designs = Design.search([
                ('category_id', '=', category.id),
                ('is_published', '=', True),
            ])
            for design in direct_designs:
                all_designs.append({
                    'type': 'design',
                    'id': design.id,
                    'name': design.name,
                    'image': bool(design.image),
                })
            
            subcategories = Category.search([
                ('parent_id', '=', category.id),
                ('is_published', '=', True),
            ])
            for subcat in subcategories:
                sub_designs = Design.search([
                    ('category_id', '=', subcat.id),
                    ('is_published', '=', True),
                ])
                for design in sub_designs:
                    all_designs.append({
                        'type': 'design',
                        'id': design.id,
                        'name': design.name,
                        'image': bool(design.image),
                    })
            
            if all_designs:
                groups.append({
                    'type': 'category',
                    'name': category.name,
                    'total': len(all_designs),
                    'items': all_designs,
                })

        products = Product.search([
            ('is_published', '=', True),
            ('design_ok', '=', True),
        ])
        
        for product in products:
            designs = product.design_ids.filtered(lambda d: d.is_published)
            if designs:
                items = [{
                    'type': 'design',
                    'id': d.id,
                    'name': d.name,
                    'image': bool(d.image),
                } for d in designs]
                
                groups.append({
                    'type': 'product',
                    'name': product.name,
                    'total': len(designs),
                    'items': items,
                })


        return {'groups': groups}
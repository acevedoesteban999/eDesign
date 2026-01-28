from odoo import http, _
from odoo.http import request
import json
from odoo.addons.e_design_website.controllers.controllers import _DOMAINES


class TvCatalog(http.Controller):
    
    @http.route('/tv/catalog', type='http', auth='user', website=True)
    def tv_catalog(self):
        
        groups = []
        
        Category = request.env['product.edesign.category'].sudo()
        categories = Category.search(_DOMAINES['product.edesign.category'])
        
        for cat in categories:
            designs = request.env['product.edesign'].sudo().search([
                ('category_id', '=', cat.id),
                ('is_published', '=', True),
            ], limit=8)
            
            if designs:
                groups.append({
                    'type': 'category',
                    'name': cat.name,
                    'total': len(designs),
                    'items': [{
                        'id': d.id, 
                        'name': d.name, 
                        'image': bool(d.image)
                    } for d in designs],
                })
        
        
        Product = request.env['product.template'].sudo()
        products = Product.search(_DOMAINES['product.template'], limit=20)
        
        for product in products:
            designs = product.design_ids.filtered(lambda d: d.is_published)
            if designs:
                groups.append({
                    'type': 'product',
                    'name': product.name,
                    'total': len(designs),
                    'items': [{
                        'id': d.id, 
                        'name': d.name, 
                        'image': bool(d.image)
                    } for d in designs],
                })
        
        return request.render('e_design_website_tv_catalog.TVCatalog', {
            'title': _("Catalog"),
            'tv_groups': json.dumps(groups),
            'config': json.dumps({
                'autoplay': 3000,
            })
        })
    
    
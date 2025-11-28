from odoo import http , _
import json

class ProductDesign(http.Controller):
    
    @http.route([
        "/catalog",
    ], type='http', auth='public',website=True)    
    def products(self,category=False, **kw):
        products = http.request.env['product.template'].search([('design_ok','=',True)])
        return http.request.render(
            'e_website_design.CatalogProducts',
            {
                'products': products
            },
        )
    @http.route([
        "/catalog/product/<model('product.template'):product>",
    ], type='http', auth='public',website=True)    
    def designs(self,product,**kw):
        referer = http.request.httprequest.headers.get('Referer', '/')
        controller_context = {
            'back_url': referer if referer != http.request.httprequest.url else '/catalog',
            'breadcrumbs':[
                {
                    'name':'Catalog',
                    'href':'/catalog'
                },
                {
                    'name':product.name,
                    'href':False
                }
            ],
            'product_id':product.id
        }
        return http.request.render(
            'e_website_design.CatalogDesigns',
            {
                'controller_context': json.dumps(controller_context), 
            },
        )
    
    @http.route("/design/<model('product.design'):design>", type='http', auth='public',website=True)    
    def design(self, design,**kw):
        return http.request.render(
            'e_website_design.CatalogDesign',
            {
                'object': http.request.env['product.design'].search([('id','=',design.id)]),
            },
        )
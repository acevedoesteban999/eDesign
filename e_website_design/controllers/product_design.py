from odoo import http , _
import json

class ProductDesign(http.Controller):
    
    @http.route([
        "/catalog",
    ], type='http', auth='public',website=True)    
    def catalog(self, **kw):
        
        return http.request.render(
            'e_website_design.CatalogPage',
            {},
        )
    @http.route([
        "/catalog/products",
    ], type='http', auth='public',website=True)    
    def products(self,category=False, **kw):
        products = http.request.env['product.template'].search([('design_ok','=',True)])
        referer = http.request.httprequest.headers.get('Referer', '/')
        breadcrumbs_context = {
            'back_url': referer if referer != http.request.httprequest.url else '/catalog',
            'breadcrumbs':[
                {'name':_('Catalog'),      'href':'/catalog'},
                {'name':_('Products'),     'href':False},
            ],
        }
        return http.request.render(
            'e_website_design.CatalogProducts',
            {
                'breadcrumbs_context':breadcrumbs_context,
                'products': products
            },
        )
    @http.route([
        "/catalog/categories",
    ], type='http', auth='public',website=True)    
    def categories(self,category=False, **kw):
        categories = http.request.env['product.design.category'].search([])
        referer = http.request.httprequest.headers.get('Referer', '/')
        breadcrumbs_context = {
            'back_url': referer if referer != http.request.httprequest.url else '/catalog',
            'breadcrumbs':[
                {'name':_('Catalog'),      'href':'/catalog'},
                {'name':_('Categories'),   'href':False},
            ],
        }
        return http.request.render(
            'e_website_design.CatalogCategories',
            {
                'breadcrumbs_context':breadcrumbs_context,
                'categories': categories
            },
        )
        
    @http.route([
        "/catalog/designs",
    ], type='http', auth='public',website=True)    
    def designs(self,**kw):
        product = category = False
        try:
            if product := kw.get('pid'):
                product = http.request.env['product.template'].browse(int(product)).read(['name','id'])[0]
                
            if category := kw.get('cid'):
                category = http.request.env['product.design.category'].browse(int(category)).read(['name','id'])[0]
        except:
            pass
        referer = http.request.httprequest.headers.get('Referer', '/')
        breadcrumbs_context = {
            'back_url': referer if referer != http.request.httprequest.url else '/catalog',
            'breadcrumbs':[
                {'name':_('Catalog'),                                  'href':'/catalog'},
                {'name':product.get('name'),     'href':('/catalog/product/%s' % product.get('id'))} if product else {},
                {'name':category.get('name'),   'href':('/catalog/categories/%s' % category.get('id'))} if category else {},
                {'name':_('Designs'),                                  'href':False,},
            ],
        }
            
        controller_context = {
            'product': product,
            'category':category,
        }
        return http.request.render(
            'e_website_design.CatalogDesigns',
            {
                'breadcrumbs_context':breadcrumbs_context,
                'controller_context': json.dumps(controller_context), 
            },
        )
    
    @http.route("/catalog/design/<model('product.design'):design>", type='http', auth='public',website=True)    
    def design(self,design,**kw):
        if design:
            product = category = False
            referer = http.request.httprequest.headers.get('Referer', '/')
            try:
                if product := kw.get('pid'):
                    product = http.request.env['product.template'].browse(int(product)).read(['name','id'])[0]
                    
                if category := kw.get('cid'):
                    category = http.request.env['product.design.category'].browse(int(category)).read(['name','id'])[0]
            except:
                pass
            breadcrumbs_context = {
                'back_url': referer if referer != http.request.httprequest.url else '/catalog',
                'breadcrumbs':[
                    {'name':_('Catalog'),              'href':'/catalog'},
                    {'name':product.get('name'),    'href':f'/catalog/designs?pid={product.get('id')}'} if product else {},
                    {'name':category.get('name'),    'href':f'/catalog/designs?cid={category.get('id')}'} if category else {},
                    {'name':design.name,            'href':False },
                ],
            }
            
            return http.request.render(
                'e_website_design.CatalogDesign',
                {
                    'design': design,
                    'breadcrumbs_context':breadcrumbs_context,
                },
            )
        else:
            return http.request.not_found()
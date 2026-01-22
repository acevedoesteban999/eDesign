from odoo import http, _
import json

EDESIGN_DOMAIN = [
    ('is_published','=',True),
]
CATEGORY_DOMAIN = [
    ('design_ids','!=',False),
] + EDESIGN_DOMAIN

PRODUCT_DOMAIN = [
    ('design_ok','=',True),
    ('design_ids','!=',False),
]

class Breadcrumb:
    def __init__(self, request: str, defaul_back_url:str, breadcrumbs: list):
        referer = request.httprequest.headers.get('Referer', '/')
        self.back_url = referer if referer != request.httprequest.url else defaul_back_url,
        self.breadcrumbs = [{
            'name': breadcrumb_name,
            'href': breadcrumb_href,
        } for breadcrumb_name, breadcrumb_href in breadcrumbs] 
        
    def _dict(self):
        return {
            'back_url': self.back_url,
            'breadcrumbs': self.breadcrumbs,
        }

class ProductDesign(http.Controller):
    
    @http.route('/e_design_website/searchRead', type='json', auth='public', website=True)
    def search_read_public(self, model, domain=None, fields=None, limit=None, **kwargs):
        allowed_models = ['product.template', 'product.edesign', 'product.edesign.category'] 
        if model not in allowed_models:
            return {'error': 'Model not allowed'}
        
        _domain = []
        
        if model == 'product.edesign':
            _domain.extend(EDESIGN_DOMAIN)
        elif model == 'product.edesign.category':
            _domain.extend(CATEGORY_DOMAIN)
        elif model == 'product.template':
            _domain.extend(PRODUCT_DOMAIN)
        
        return http.request.env[model].sudo().search_read(
            domain = (domain + _domain) or _domain,
            fields=fields or ['id'],
            limit=limit
        )
        
        
    
    @http.route("/designs", type='http', auth='public', website=True)    
    def designs(self, **kw):
        return http.request.render(
            'e_design_website.DesignsPage',
            {
                'title': _("Design Catalog"),
            },
        )
        
    @http.route([
        "/designs/products",
        "/designs/products/<model('product.template'):product>",
    ], type='http', auth='public', website=True)    
    def products(self, product=False, **kw):
        if product:
            products = product
        else:
            products = http.request.env['product.template'].search(PRODUCT_DOMAIN)
        
        
        breadcrumb_manager = Breadcrumb(
            http.request,
            '/designs',
            [
                (_('Designs'), '/designs'),
                (_('Products'), False),
            ]
        )
        
        return http.request.render(
            'e_design_website.DesignsProducts',
            {
                'title': _("Products"),
                'breadcrumbs_context': breadcrumb_manager._dict(),
                'products': products,
            },
        )
        
    @http.route([
        "/designs/ecategories",
        "/designs/ecategories/<model('product.edesign.category'):category>"
    ], type='http', auth='public', website=True)    
    def categories(self, category=False, **kw):
        if category:
            categories = category
        else:
            categories = http.request.env['product.edesign.category'].search([CATEGORY_DOMAIN])
            
        breadcrumb_manager = Breadcrumb(
            http.request,
            '/designs',
            breadcrumbs=[
                (_('Catalog'), '/catalog'),
                (_('Categories'), False),
            ]
        )
        
        return http.request.render(
            'e_design_website.DesignsCategories',
            {
                'title': _("Categories"),
                'breadcrumbs_context': breadcrumb_manager._dict(),
                'categories': categories,
            },
        )
        
    @http.route([
        "/designs/edesigns",
        "/designs/edesigns/<model('product.template'):product>",
        "/designs/edesigns/<model('product.edesign.category'):category>",
    ], type='http', auth='public', website=True)    
    def designs_list(self, product=False, category=False, **kw):
        breadcrumbs_data = [(_('Designs'), '/designs')]
        
        if product:
            breadcrumbs_data.append((product.name, f'/designs/product/{product.id}'))
        if category:
            breadcrumbs_data.append((category.name, f'/designs/ecategory/{category.id}'))
        
        breadcrumbs_data.append((_('Designs'), False))
        
        breadcrumb_manager = Breadcrumb(
            http.request,
            '/designs',
            breadcrumbs=breadcrumbs_data
        )
            
        controller_context = {
            'product': product.id if product else False,
            'category': category.id if category else False,
        }
        
        return http.request.render(
            'e_design_website.EProductDesignTemplate',
            {
                'title': _("Designs"),
                'breadcrumbs_context': breadcrumb_manager._dict(),
                'controller_context': json.dumps(controller_context), 
            },
        )
    
    @http.route([
        "/designs/design/<model('product.edesign'):design>",
        "/designs/design/<model('product.template'):product/<model('product.edesign'):design>",
        "/designs/design/<model('product.edesign.category'):category/<model('product.edesign'):design>",
    ], type='http', auth='public', website=True)    
    def design_detail(self, design ,product , category, **kw):
        if not design:
            return http.request.not_found()
            
        
        breadcrumbs_data = []
        
        breadcrumbs_data.append((_('Catalog'), '/designs'))
        if product:
            breadcrumbs_data.append((_('Products'), '/designs/products'))
            breadcrumbs_data.append((product.name, f'/designs/products/{product.id}'))
        elif category:
            breadcrumbs_data.append((_('Categories'), '/designs/ecategories'))
            breadcrumbs_data.append((category.name, f'/designs/ecategories/{category.id}'))
        
        
        breadcrumbs_data.append((design.name, False))
        
        breadcrumb_manager = Breadcrumb(
            http.request,
            '/designs',
            breadcrumbs=breadcrumbs_data
        )
        
        return http.request.render(
            'e_design_website.DesignsDesign',
            {
                'title': _("Design %s" % design.name),
                'design': design,
                'breadcrumbs_context': breadcrumb_manager._dict(),
            },
        )
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
        
        
    
    @http.route("/edesigns", type='http', auth='public', website=True)    
    def designs(self, **kw):
        return http.request.render(
            'e_design_website.DesignsPage',
            {
                'title': _("Designs"),
            },
        )
        
    @http.route([
        "/edesigns/products",
    ], type='http', auth='public', website=True)    
    def products(self, product=False, **kw):
        
        products = http.request.env['product.template'].search(PRODUCT_DOMAIN)
        
        breadcrumb_manager = Breadcrumb(
            http.request,
            '/edesigns',
            [
                ('Home', '/edesigns'),
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
        "/designs/categories",
    ], type='http', auth='public', website=True)    
    def categories(self, category=False, **kw):
    
        categories = http.request.env['product.edesign.category'].search([CATEGORY_DOMAIN])
            
        breadcrumb_manager = Breadcrumb(
            http.request,
            '/edesigns',
            breadcrumbs=[
                ('Home', '/edesigns'),
                (_('Catrgories'), False),
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
        "/edesigns/<model('product.edesign'):design>",
        "/edesigns/products/<model('product.template'):product/<model('product.edesign'):design>",
        "/edesigns/categories/<model('product.edesign.category'):category/<model('product.edesign'):design>",
    ], type='http', auth='public', website=True)    
    def design_detail(self, design ,product = False , category = False, **kw):
        if not design:
            return http.request.not_found()
            
        
        breadcrumbs_data = []
        
        breadcrumbs_data.append(('Home', '/edesigns'))
        if product:
            breadcrumbs_data.append((_('Products'), '/edesigns/products'))
        elif category:
            breadcrumbs_data.append((_('Categories'), '/edesigns/categories'))
        else:
            breadcrumbs_data.append((_('Designs'), '/edesigns/designs'))
        
        breadcrumbs_data.append((design.name, False))
        
        breadcrumb_manager = Breadcrumb(
            http.request,
            '/edesigns',
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
        
        
    @http.route([
        "/edesigns/designs",
        "/edesigns/products/<model('product.template'):product>/",
        "/edesigns/catrgories/<model('product.edesign.category'):category>/",
    ], type='http', auth='public', website=True)    
    def designs_list(self, product=False, category=False, **kw):
        breadcrumbs_data = [
            ('Home', '/edesigns'),
        ]
        final_space = True
        if product:
            breadcrumbs_data.append((_("Products"), f'/edesigns/products'))
        elif category:
            breadcrumbs_data.append((_("Categories"), f'/edesigns/ecategories'))
        else:
            breadcrumbs_data.append((_('Designs'), False))
            final_space = False
        
        if final_space:
            breadcrumbs_data.append((' ', False))
        
        breadcrumb_manager = Breadcrumb(
            http.request,
            '/edesigns',
            breadcrumbs=breadcrumbs_data
        )
            
        controller_context = {
            'product': product.read(['name','design_ids'])[0] if product else False,
            'category': category if category else False,
        }
        
        return http.request.render(
            'e_design_website.EProductDesignTemplate',
            {
                'title': _("Designs"),
                'breadcrumbs_context': breadcrumb_manager._dict(),
                'controller_context': json.dumps(controller_context), 
            },
        )
    
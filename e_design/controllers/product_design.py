from odoo import http , _


class ProductDesign(http.Controller):
    @http.route([
        "/designs",
        "/designs/page/<int:page>",
        "/designs/catrgory/<model('product.design.category'):category>",
    ], type='http', auth='public',website=True)    
    def designs(self,category=None, **kw):
        domain = []
        if category:
            domain += [('category_id','=',category.id)]
        return http.request.render(
            'e_design.designs',
            {
                'objects': http.request.env['product.design'].search(domain),
            },
        )
    @http.route("/design/<design('product.design')>", type='http', auth='public',website=True)    
    def design(self, design,**kw):
        return http.request.render(
            'e_design.design',
            {
                'object': http.request.env['product.design'].search([('id','=',design.id)]),
            },
        )
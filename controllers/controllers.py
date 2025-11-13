from odoo import http


class Controllers(http.Controller):
    @http.route(['/general','/main'], type='http', auth='public',website=True)
    def catalog(self, **kw):
        return http.request.render('e_sublimation.MainComponent')
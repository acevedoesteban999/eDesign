from odoo import models , fields , api
class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    is_published = fields.Boolean("Is Published",help="Is Published on Website",default=True)
    
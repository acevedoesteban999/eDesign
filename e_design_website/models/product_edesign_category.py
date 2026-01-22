from odoo import models , fields

class ProductEDesign(models.Model):
    _inherit = "product.edesign.category"
    
    is_published = fields.Boolean("Is Published",help="Is Published on Website",default=True)
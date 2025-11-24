from odoo import models,fields

class ProductAttribute(models.Model):
    _inherit = "product.attribute"
    
    sublimation_ok = fields.Boolean(default=False)
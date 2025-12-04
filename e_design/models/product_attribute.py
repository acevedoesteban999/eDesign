from odoo import models,fields

class ProductAttribute(models.Model):
    _inherit = "product.attribute"
    
    design_ok = fields.Boolean(default=False)
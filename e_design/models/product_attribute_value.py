from odoo import models,fields

class ProductAttribute(models.Model):
    _inherit = "product.attribute.value"
    
    without_design_ok = fields.Boolean(default=False)
    product_design_id = fields.Many2one('product.design',"Design")

class ProductAttribute(models.Model):
    _inherit = "product.template.attribute.line"
    
    design_ok = fields.Boolean(related='attribute_id.design_ok')
    
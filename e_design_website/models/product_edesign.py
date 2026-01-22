from odoo import models , fields

class ProductEDesign(models.Model):
    _inherit = "product.edesign"
    
    is_published = fields.Boolean("Is Published",help="Is Published on Website",default=True)
    
    product_ids = fields.Many2many('product.template','rel_product_edesigns',compute="_compute_product_ids",precompute=True)
    
    
    def _compute_product_ids(self):
        for rec in self:
            rec.product_ids = self.env['product.template'].search([('design_ids','in',rec.id)])    
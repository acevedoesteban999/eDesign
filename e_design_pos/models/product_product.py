from odoo import _, api, fields, models


class ModuleName(models.Model):
    _inherit = 'product.product'
    
    has_design = fields.Boolean(related='product_tmpl_id.design_ok')
    design_ids = fields.Many2many(related='product_tmpl_id.design_ids')
from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'SaleOrder'

    has_design = fields.Boolean(compute='_compute_has_design')
    
    
    @api.depends('order_line')
    def _compute_has_design(self):
        for rec in self:
            rec.has_design = any(rec.order_line.mapped('design_id'))
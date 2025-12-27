from odoo import models, fields, api, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _description = 'SaleOrderLine'

    design_id = fields.Many2one('product.design',"Design",compute='_compute_design_id')
    
    def _compute_design_id(self):
        for rec in self:
            design = rec.product_no_variant_attribute_value_ids.filtered_domain([('attribute_id.design_ok','=',True)])
            rec.design_id = design and design[0].product_attribute_value_id.product_design_id.id or False
from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'account.move.line'
    _description = 'SaleOrderLine eDesign'

    design_id = fields.Many2one('product.design',"Design",compute='_compute_design_id')
    
    def _compute_design_id(self):
        for rec in self:
            design = False
            try:
                design = rec.sale_line_ids[0].product_no_variant_attribute_value_ids.filtered_domain([('attribute_id.design_ok','=',True)])
            except:
                pass
            rec.design_id = design and design[0].product_attribute_value_id.product_design_id.id or False
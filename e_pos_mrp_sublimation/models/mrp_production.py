# -*- coding: utf-8 -*-
from odoo import models,fields,api


class MrpProduction(models.Model):
    
    _inherit = 'mrp.production'
    
    design_id = fields.Many2one('product.design',"Design",compute="_compute_design_id",store=True)
    
    @api.depends('pos_order_line_id','sale_line_id')
    def _compute_design_id(self):
        for rec in self:
            design = False
            if rec.pos_order_line_id:
                design = rec.pos_order_line_id.attribute_value_ids.filtered_domain([('attribute_id.sublimation_ok','=',True)])
                design = design and design[0].product_attribute_value_id.product_design_id or False
            elif rec.sale_line_id:
                design = rec.sale_line_id.product_no_variant_attribute_value_ids.filtered_domain([('attribute_id.sublimation_ok','=',True)])
                design = design and design[0].product_attribute_value_id.product_design_id or False
            
            
            rec.design_id = design
            
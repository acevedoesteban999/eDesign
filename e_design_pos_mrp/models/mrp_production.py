# -*- coding: utf-8 -*-
from odoo import models,fields,api


class MrpProduction(models.Model):
    
    _inherit = 'mrp.production'
    
    design_id = fields.Many2one('product.design',"Design")
    has_design_id = fields.Boolean(compute="_compute_design_id")
    domain_design = fields.Char(compute="_compute_design_id")
    
    @api.depends('product_id','pos_order_line_id','sale_line_id')
    def _compute_design_id(self):
        for rec in self:
            design = rec.design_id or False
            domain_design = []
            if rec.pos_order_line_id:
                design = rec.pos_order_line_id.attribute_value_ids.filtered_domain([('attribute_id.design_ok','=',True)])
                design = design and design[0].product_attribute_value_id.product_design_id or False
            elif rec.sale_line_id:
                design = rec.sale_line_id.product_no_variant_attribute_value_ids.filtered_domain([('attribute_id.design_ok','=',True)])
                design = design and design[0].product_attribute_value_id.product_design_id or False
            elif rec.product_id.product_tmpl_id.design_ok:
                domain_design = [('id', 'in', rec.product_id.product_tmpl_id.design_ids.ids)]
            
            rec.has_design_id = True if design or domain_design else False
            rec.domain_design = str(domain_design)
            rec.design_id = design
            
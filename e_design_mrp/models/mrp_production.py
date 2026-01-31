# -*- coding: utf-8 -*-
from odoo import models,fields,api


class MrpProduction(models.Model):
    
    _inherit = 'mrp.production'
    
    design_id = fields.Many2one('product.edesign',"Design",compute="_compute_design_id",store=True,readonly=False)
    has_design_id = fields.Boolean(compute="_compute_has_design_id")
    product_tmpl_designs_ids = fields.Many2many(related='product_tmpl_id.design_ids')
    
    def _compute_has_design_id(self):
        for rec in self:
            rec.has_design_id = rec.product_tmpl_id.design_ok and rec.product_tmpl_id.design_ids
    
    def _check_design_routes(self):
        if self.sale_line_id:
            self.design_id = self.sale_line_id.design_id.id
        else:
            self.design_id = False
    
    
    def _compute_design_id(self):
        for rec in self:
            if rec.has_design_id and not rec.design_id:
                rec._check_design_routes()
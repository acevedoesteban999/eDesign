# -*- coding: utf-8 -*-
from odoo import models,fields,api


class MrpProduction(models.Model):
    
    _inherit = 'mrp.production'
    
    
    def _check_design_routes(self):
        if self.pos_order_line_id:
            self.design_id = self.pos_order_line_id.design_id
    
    @api.depends('pos_order_line_id')
    def _compute_design_id(self):
        super()._compute_design_id()
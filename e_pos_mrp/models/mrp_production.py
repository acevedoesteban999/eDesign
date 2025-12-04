# -*- coding: utf-8 -*-
from odoo import models,fields


class MrpProduction(models.Model):
    
    _inherit = 'mrp.production'
    
    pos_order_id = fields.Many2one('pos.order',"Origin POS",compute="_compute_pos_order_line")
    pos_order_line_id = fields.Many2one('pos.order.line',"Origin POS line")
    
    def _compute_pos_order_line(self):
        for rec in self:
            rec.pos_order_id = rec.pos_order_line_id.order_id
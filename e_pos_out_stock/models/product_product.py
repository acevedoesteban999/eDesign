# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    can_show_in_pos_out_stock = fields.Boolean(compute="_compute_can_show_in_pos_out_stock")
    
    def _compute_can_show_in_pos_out_stock(self):
        for rec in self:
            rec.can_show_in_pos_out_stock = rec.product_tmpl_id.show_pos_outofstock or rec.product_tmpl_id.pos_categ_ids.get_show_pos_outofstock_recursive()
    
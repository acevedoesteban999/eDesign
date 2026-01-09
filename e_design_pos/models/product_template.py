# -*- coding: utf-8 -*-
from odoo import models, fields



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    show_pos_outofstock = fields.Boolean("Show products in POS with Out of Stock")
    can_show_in_pos_out_stock = fields.Boolean(compute="_compute_can_show_in_pos_out_stock")
    
    def _compute_can_show_in_pos_out_stock(self):
        for rec in self:
            rec.can_show_in_pos_out_stock = rec.show_pos_outofstock or rec.pos_categ_ids.get_show_pos_outofstock_recursive()
        
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    has_create_pos_mrp = fields.Boolean(
        compute="_compute_has_create_pos_mrp")
    
    def _compute_has_create_pos_mrp(self):
        for rec in self:
            rec.has_create_pos_mrp = rec.product_tmpl_id.can_create_pos_mrp
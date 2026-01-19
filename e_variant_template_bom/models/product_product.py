# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ , Command
from odoo.exceptions import UserError, ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    combination_value_indices = fields.Char(compute='_compute_combination_indices', store=True, index=True)
    
    @staticmethod
    def _ids2str(records,):
        return ','.join([str(i) for i in sorted(records.ids)])
    
    @api.depends('product_template_attribute_value_ids')
    def _compute_combination_indices(self):
        for rec in self:
            super(ProductProduct,rec)._compute_combination_indices()
            rec.combination_value_indices = self._ids2str(rec.product_template_attribute_value_ids.product_attribute_value_id)

        
    
    
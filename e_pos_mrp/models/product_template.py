# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    can_create_pos_mrp = fields.Boolean(
        string='Manufacture on demand',
        help="Check if the product should make mrp order in pos. Require bill of materials for template or product.")
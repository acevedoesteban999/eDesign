# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    has_variant_template = fields.Boolean("Variant Template")
    product_variant_template = fields.Many2one('product.template',"Product Variant Template")
    auto_create_childs_variants = fields.Boolean("Create Childs Variant")
    auto_create_childs_bom = fields.Boolean("Create Childs Bom")
    
    
    @api.onchange('product_variant_template')
    def onchange_product_variant_template(self):
        pass
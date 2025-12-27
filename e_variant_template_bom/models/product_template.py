# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ , Command
from odoo.exceptions import UserError, ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    auto_create_boms = fields.Boolean("Autocreate Bom from Parent", help="'Auto create bom' only work for same variant's combination in parent template and self")
    extra_products_create_boms = fields.Many2many('product.product','rel_variant_bom_tamplate',string="Extra products for automatic bum creation")
        
    def _create_auto_bom(self):
        if not self.auto_create_boms:
            return
        combination_value_indices = self.product_variant_template.product_variant_ids.mapped('combination_value_indices')
        for variant in self.product_variant_ids.filtered_domain([('combination_value_indices','in',combination_value_indices)]):
            exist = self.bom_ids.search([
                ('product_tmpl_id','=',variant.product_tmpl_id.id),
                ('product_id','=',variant.id),
                ('type','=','normal'),
            ])
            if not exist:
                variant_parent = self.product_variant_template.product_variant_ids.filtered_domain([('combination_value_indices','=',variant.combination_value_indices)])
                if variant_parent:
                    self.bom_ids.create({
                        'product_tmpl_id': variant.product_tmpl_id.id,
                        'product_id': variant.id,
                        'product_qty': 1,
                        'type':'normal',
                        'bom_line_ids':[
                            Command.create({
                                'product_id': variant_parent.id,
                                'product_qty': 1,
                            })
                        ] + [
                        Command.create({
                                'product_id':extra_product.id,
                                "product_qty":1,
                            })  for extra_product in  self.extra_products_create_boms
                        ] 
                    })    
    
    def write(self,vals):
        resp = super().write(vals)
        if not self.is_product_variant and 'attribute_line_ids' in vals:
            for child in self.child_variant_template_ids.filtered_domain([('auto_create_boms','=',True)]):
                child._create_auto_bom()
        if not self.is_product_variant and 'auto_create_boms' in vals and vals.get('auto_create_boms'):
            self._create_auto_bom()
        return resp
    
    
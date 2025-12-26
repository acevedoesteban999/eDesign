# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ , Command
from odoo.exceptions import UserError, ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    has_variant_template = fields.Boolean("Variant Template")
    product_variant_template = fields.Many2one('product.template',"Product Variant Template")
    child_variant_template_ids = fields.One2many('product.template','product_variant_template')
    auto_create_variants = fields.Boolean("Autocreate variant from Parent")
    # auto_create_boms = fields.Boolean("Autocreate Bom from Parent")
    
    # @api.onchange('auto_create_boms')
    # def onchenge_auto_create_boms(self):
    #     if self.auto_create_boms:
            
    
    @api.onchange('product_variant_template')
    def onchange_product_variant_template(self):
        if self.has_variant_template and self.product_variant_template:
            for line in self.product_variant_template.attribute_line_ids.filtered_domain([('attribute_id.create_variant','=','always')]):
                attr = line.attribute_id
                line_values = line.value_ids.filtered_domain([('attribute_id','=',line.attribute_id.id)])
                if attr not in self.attribute_line_ids.attribute_id:
                    self.attribute_line_ids = [
                        Command.create({
                                'attribute_id': attr.id,
                                'product_tmpl_id':self.id,
                                'value_ids': [Command.link(value.id) for value in line_values]
                            })
                        
                    ]
                else:
                    self_line = self.attribute_line_ids.filtered_domain([('attribute_id','=',attr.id)])
                    add_values = line_values - self_line.value_ids._origin
                    self_line.value_ids = [
                        Command.link(value.id) for value in add_values
                    ]
                    
    
    def write(self,vals):
        resp = super().write(vals)
        if 'attribute_line_ids' in vals:
            for child in self.child_variant_template_ids.filtered_domain([('auto_create_variants','=',True)]):
                child.onchange_product_variant_template()
        return resp
     
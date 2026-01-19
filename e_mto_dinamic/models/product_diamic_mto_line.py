# -*- coding: utf-8 -*-


from odoo import models, fields, api, _

class ProductMtoDiamicLine(models.Model):
    _name = 'product.diamic.mto.line'
    _description = 'Product MTO Dinamci Line'


    parent_product_template_id = fields.Many2one('product.template')
    product_template_id = fields.Many2one('product.template','Product Template' , required=True)
    product_id = fields.Many2one('product.product','Product Variant')
    
    product_template_variant_count = fields.Integer(related='product_template_id.product_variant_count')
    
    
    _sql_constraints = [
        ('unique_products', 'unique(parent_product_template_id,product_template_id,product_id)', 'Can not duplique a combination of Products')
    ]
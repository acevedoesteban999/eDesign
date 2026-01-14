# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    generic_ok = fields.Boolean(string='Generic Product')
    generic_bill_material_ids = fields.Many2many('product.product',"rel_generic_product_product",name="Generic Bill Materials")
    
    @api.model
    def get_generic_bill_material_ids(self,product_tmpl_id):
        return self.browse(product_tmpl_id).generic_bill_material_ids.read(['name'])
    
    @api.model
    def get_generic_final_price(self):
        self.ensure_one()
        return sum(self.generic_bill_material_ids.lst_price)
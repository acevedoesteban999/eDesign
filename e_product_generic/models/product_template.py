# -*- coding: utf-8 -*-
from odoo import models, fields, api, _ , exceptions

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    generic_ok = fields.Boolean(string='Generic Product')
    generic_bill_material_ids = fields.Many2many('product.product',"rel_generic_product_product",name="Generic Bill Materials")
    
    currency_symbol = fields.Char(related='currency_id.symbol')
    currency_position = fields.Selection(related='currency_id.position')

    @api.constrains('generic_ok','generic_bill_material_ids')
    def check_generic_ok(self):
        for rec in self:
            if rec.generic_ok and not rec.generic_bill_material_ids:
                raise exceptions.UserError(_("Generic Products Requiere a Generic Bill of Materials"))
            
    @api.model
    def get_generic_bill_material_data(self,product_tmpl_id):
        return self.browse(product_tmpl_id).generic_bill_material_ids.read(['display_name','standard_price'])
        
    @api.model
    def get_generic_final_price(self):
        self.ensure_one()
        return sum(self.generic_bill_material_ids.lst_price)
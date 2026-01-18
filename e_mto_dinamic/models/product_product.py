# -*- coding: utf-8 -*-
from odoo import models, fields, api, _ , exceptions

class ProductTemplate(models.Model):
    _inherit = 'product.product'

    @api.model
    def get_dinamic_bill_material_data(self,_product_id):
        _dinamic_bill_material_data =  self.browse(_product_id).product_tmpl_id.lines_dinamic_bill_material_ids.read(['product_template_id','product_id'])
        dinamic_bill_material_data = []
        read_fields = ['id','display_name','standard_price']
        for dinamic_bill in _dinamic_bill_material_data:
            product = product_template = product_variant_ids = False
            
            if dinamic_bill['product_id']:
                product = self.browse(dinamic_bill['product_id'][0])
                product_template = product.product_tmpl_id
            else: 
                product_template = self.product_tmpl_id.browse(dinamic_bill['product_template_id'][0])
                if product_template.product_variant_count == 1:
                    product = product_template.product_variant_id
                else:
                    product_variant_ids = product_template.product_variant_ids.read(read_fields)
                
                    
            dinamic_bill_material_data.append({
                'product': {
                    **product.read(read_fields)[0],
                } if product else False,
                'product_variant_ids': product_variant_ids,
                'product_template': {
                    **product_template.read([r for r in read_fields if r != 'standard_price'])[0],
                },
                'uid': (product_template.id , product.id if product else False)
            }) 
        return dinamic_bill_material_data
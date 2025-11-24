from odoo import fields,models,api , Command , _
from odoo.exceptions import ValidationError
class ProductProduct(models.Model):
    _inherit = 'product.template'

    sublimation_ok = fields.Boolean(string='Sublimation')
    
    @api.constrains('sublimation_ok')
    def _check_sublimation_ok(self):
        for rec in self:
            if rec.sublimation_ok:
                attr = self.env.ref('e_sublimation.default_attr_design')
                if attr.id not in rec.attribute_line_ids.attribute_id.ids:
                    rec.attribute_line_ids.create({
                        'attribute_id': attr.id,
                        'product_tmpl_id':self.id,
                        'value_ids': [Command.link(self.env.ref('e_sublimation.default_attr_value_no_design').id)]
                    })
                    rec._create_variant_ids()
                    
    
    
    

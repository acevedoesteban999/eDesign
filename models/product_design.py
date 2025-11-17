from odoo import models , fields , api

class ProductDesign(models.Model):
    _name = 'product.design'
    
    name = fields.Char("Name")
    image = fields.Image("Image")
    product_attribute_o2m = fields.One2many('product.attribute.value','product_design_id','Attr Value')
    product_attr_value_id = fields.Many2one('product.attribute.value',compute="_compute_product_attr_value_id")
    
    @api.depends('product_attribute_o2m')
    def _compute_product_attr_value_id(self):
        for rec in self:
            rec.product_attr_value_id = rec.product_attribute_o2m and rec.product_attribute_o2m[0].id or rec.product_attribute_o2m
    
    
    @api.model
    def get_data_for_product_template_view(self,*args,**kwargs):
        line_id = self.env['product.template.attribute.line'].browse(args).filtered_domain([('attribute_id.sublimation_ok','=',True)])
        line_id = line_id and line_id[0] or line_id
        value_ids = line_id.value_ids.filtered_domain([('without_design_ok','=',False)])
        return value_ids.read([
            'name',
            'default_extra_price',
            'product_design_id',
        ])
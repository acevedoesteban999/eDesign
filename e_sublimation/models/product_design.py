from odoo import models , fields , api , Command
from odoo.exceptions import ValidationError

class ProductDesign(models.Model):
    _name = 'product.design'
    
    name = fields.Char(string="Name",related="product_attr_value_id.name",readonly=False)
    image = fields.Image("Image")
    default_code = fields.Char('Internal Reference')
    
    extra_price = fields.Float("Extra Price",related='product_attr_value_id.default_extra_price',readonly=False)
    product_attr_value_id = fields.Many2one('product.attribute.value')
    product_id = fields.Many2one('product.template',store=False,domain=[('sublimation_ok','=',True)])
    
    @api.model
    def get_data_for_product_template_view(self,*args,**kwargs):
        line_id = self.env['product.template.attribute.line'].browse(args).filtered_domain([('attribute_id.sublimation_ok','=',True)])
        line_id = line_id and line_id[0] or line_id
        value_ids = line_id.value_ids.filtered_domain([('without_design_ok','=',False)])
        return value_ids.product_design_id.read([
            'id',
            'name',
            'default_code',
            'extra_price',
        ])
    
    @api.model
    def get_design_action(self,*args,**kwargs):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Designs',   
            'res_model': 'product.design',   
            'view_type': 'form',    
            'view_mode': 'form',   
            'res_id': kwargs.get('product_design_id'),
            'views':[(self.env.ref('e_sublimation.product_design_view_form').id,'form')],
            'target': 'new',
            'domain':[],
            'context':{
                **kwargs
            } 
        }
    
    
    def create(self,vals_list:dict):
        product_id = self.env.context.get('product_id') or vals_list.get('product_id')
        if not product_id:
            raise ValidationError(f"No Product in Context: {product_id}")
        line_id =self.env['product.template'].browse(product_id).attribute_line_ids.filtered_domain([('attribute_id.sublimation_ok','=',True)])
        
        line_id = len(line_id) > 1 and line_id[0] or line_id
        if not line_id:
            raise ValidationError(f"No Sublimation Design Line in product: {product_id}")
        
        new_attr_value = self.env['product.attribute.value'].create({
            'name': vals_list.get('name','Sublimation Design'),
            'attribute_id': self.env.ref('e_sublimation.default_attr_design').id,
            'default_extra_price':vals_list.get('extra_price')
        })
        
        line_id.value_ids = [Command.link(new_attr_value.id)]
        
        vals_list['product_attr_value_id'] = new_attr_value.id
        record =  super().create(vals_list)
        new_attr_value.product_design_id = record.id
        return record
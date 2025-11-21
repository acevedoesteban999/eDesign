from odoo import models , fields , api , Command

class ProductDesign(models.Model):
    _name = 'product.design'
    
    name = fields.Char("Name")
    image = fields.Image("Image")
    extra_price = fields.Float("Extra Price",store=False)
    
    #product_attr_value_id = fields.Many2one('product.attribute.value')
    # @api.depends('product_attribute_o2m')
    # def _compute_product_attr_value_id(self):
    #     for rec in self:
    #         rec.product_attr_value_id = rec.product_attribute_o2m and rec.product_attribute_o2m[0].id or rec.product_attribute_o2m
    
    
    @api.model
    def get_data_for_product_template_view(self,*args,**kwargs):
        line_id = self.env['product.template.attribute.line'].browse(args).filtered_domain([('attribute_id.sublimation_ok','=',True)])
        line_id = line_id and line_id[0] or line_id
        value_ids = line_id.value_ids.filtered_domain([('without_design_ok','=',False)])
        return value_ids.read([
            'id',
            'name',
            'default_extra_price',
            'product_design_id',
        ])
    
    @api.model
    def get_design_action(self,*args,**kwargs):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Designs',   
            'res_model': 'product.design',   
            'view_type': 'form',    
            'view_mode': 'form',   
            'views':[(self.env.ref('e_sublimation.product_design_view_form').id,'form')],
            'target': 'new',
            'domain':[],
            'context':{
                **kwargs
            } 
        }
    
    
    def create(self,vals_list:dict):
        product_id = self.env.context.get('product_id')
        if not product_id:
            return
        line_id =self.env['product.template'].browse(product_id).attribute_line_ids.filtered_domain([('attribute_id.sublimation_ok','=',True)])
        
        line_id = len(line_id) > 1 and line_id[0] or line_id
        if not line_id:
            return
        
        new_attr_value = self.env['product.attribute.value'].create({
            'name': vals_list.get('name','Sublimation Design'),
            'attribute_id': self.env.ref('e_sublimation.default_attr_design').id,
            'default_extra_price':self.extra_price
        })
        
        line_id.value_ids = [Command.link(new_attr_value.id)]
        
        
        record =  super().create(vals_list)
        new_attr_value.product_design_id = record.id
        return record
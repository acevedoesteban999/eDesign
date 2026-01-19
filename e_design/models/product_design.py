from odoo import models , fields , api , Command
from odoo.exceptions import ValidationError
from ..utils.utils import get_datas_m2m

class ProductDesign(models.Model):
    _name = 'product.design'
    
    name = fields.Char(string="Name",required=True)
    image = fields.Image("Image")
    default_code = fields.Char('Internal Reference',required=True)
    
    extra_price = fields.Float("Extra Price",related='product_attr_value_id.default_extra_price',readonly=False)
    product_attr_value_id = fields.Many2one('product.attribute.value')
    
    attr_value_ids = fields.One2many('product.attribute.value','product_design_id',"Attr Value Lines")
    product_ids = fields.Many2many('product.template',domain=[('design_ok','=',True)],string="Products")
    products_counter = fields.Integer("In Porducts",compute="_compute_product_ids")
    category_id = fields.Many2one('product.design.category',"Category")
    
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string="Attachments",
        store=True,
        readonly=False,
    )
    file_id = fields.Binary("File")
            
    @api.depends('attr_value_ids')       
    def _compute_product_ids(self):
        for rec in self:
            products = self.env['product.template.attribute.value'].search([('product_attribute_value_id','in',rec.attr_value_ids.ids)]).attribute_line_id.product_tmpl_id
            rec.product_ids = [Command.clear()] + [Command.link(product.id) for product in products]
            rec.products_counter = len(rec.product_ids)
        
    @api.model
    def get_data_for_product_template_view(self,*args,**kwargs):
        line_id = self.env['product.template.attribute.line'].browse(args).filtered_domain([('attribute_id.design_ok','=',True)])
        line_id = line_id and line_id[0] or line_id
        value_ids = line_id.value_ids.filtered_domain([('without_design_ok','=',False)])
        return self.search_read(
            [('id','in',value_ids.product_design_id.ids)],
            ['id','name','default_code','extra_price'],
            limit=4,
            order='id desc',
        )
    
    def _get_base_design_action(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Crete Design',   
            'res_model': 'product.design',   
            'view_type': 'form',    
            'view_mode': 'form',   
            'res_id': False,
            'views':[(self.env.ref('e_design.product_design_view_form').id,'form')],
            'target': 'new',
            'domain':[], 
            'context':{},
        }
    
    @api.model
    def get_open_design_action(self,*args,**kwargs):
        return {
            **self._get_base_design_action(),
            'res_id': kwargs.get('product_design_id'),
        }
    
    @api.model
    def get_create_design_action(self,*args,**kwargs):
        return {
            **self._get_base_design_action(),
            'context':{
                'default_product_ids':[Command.link(kwargs.get('product_id'))],
            } 
        }
    
    @api.model
    def get_unlink_design_action(self,*args,**kwargs):
        return{
            **self._get_base_design_action(),
            'res_model': 'e_design.product_design_unlink_widget',   
            'views':[(self.env.ref('e_design.product_design_unlink_view_form').id,'form')],
            'context': {
                **kwargs,
            }
        } 
        
    @api.model
    def get_attach_design_action(self,*args,**kwargs):
        return{
            **self._get_base_design_action(),
            'res_model': 'e_design.product_design_attach_widget',   
            'views':[(self.env.ref('e_design.product_design_attach_view_form').id,'form')],
            'context': {
                **kwargs,
            }
        } 
        
        
    
    
    
            
    def write(self,vals):
        
        if _att := vals.get('attachment_ids'):
            att_add, att_sub = get_datas_m2m(_att)
            if att_add:
                self.env['ir.attachment'].browse(att_add).public=True
            if att_sub:
                self.env['ir.attachment'].browse(att_sub).unlink()
        
        def __get_value_id(product_id):
            line_id =self.env['product.template'].browse(product_id).attribute_line_ids.filtered_domain([('attribute_id.design_ok','=',True)])
            line_id = line_id and line_id[0] or line_id
            value_id =  self.env['product.attribute.value'].search([('product_design_id','=',self.id)]) 
            value_id = value_id and value_id[0] or value_id
            return line_id, value_id
        
        product_add, product_sub = get_datas_m2m(vals.get('product_ids'))

        

        for product_id in product_add:
            line_id , value_id = __get_value_id(product_id)
            if line_id:
                if not value_id:
                    value_id = self._create_value(vals.get('name',self.name),vals.get('default_code',self.default_code),vals.get('extra_price',self.extra_price))
                    value_id.product_design_id = self.id
                line_id.value_ids = [Command.link(value_id.id)]
        
        for product_id in product_sub:
            line_id , value_id = __get_value_id(product_id)
            if line_id and value_id:
                line_id.value_ids = [Command.unlink(value_id.id)]
        res =  super().write(vals)
        if 'name' in vals:
            self.attr_value_ids.name = f"[{self.default_code}] {self.name}"
        return res
    
    def _create_value(self,name,default_code,extra_price):
        return self.env['product.attribute.value'].create({
                'name': f"[{default_code}] {name}",
                'attribute_id': self.env.ref('e_design.default_attr_design').id,
                'default_extra_price':extra_price
            })
    
    def create(self,vals_list:dict):
        if _att := vals_list.get('attachment_ids'):
            att_add, _ = get_datas_m2m(_att)
            if att_add:
                self.env['ir.attachment'].browse(att_add).public=True
                
        products , _ = get_datas_m2m(vals_list.get('product_ids'))
        if products:
            attr_value = self._create_value(vals_list.get('name'),vals_list.get('default_code'),vals_list.get('extra_price'))
            
            for product_id in products:
                line_id =self.env['product.template'].browse(product_id).attribute_line_ids.filtered_domain([('attribute_id.design_ok','=',True)])
                line_id = len(line_id) > 1 and line_id[0] or line_id
                if not line_id:
                    raise ValidationError(f"No Design Design Line in product: {product_id}")
                line_id.value_ids = [Command.link(attr_value.id)]
            record =  super().create(vals_list)
                
            attr_value.product_design_id = record.id
            return record
        return  super().create(vals_list)
    
    
    def get_formview_action(self, access_uid=None):
        view_id = self.sudo().get_formview_id(access_uid=access_uid)
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'views': [(view_id, 'form')],
            'target': self._context.get('action_target') or 'current' ,
            'res_id': self.id,
            'context': dict(self._context),
        }
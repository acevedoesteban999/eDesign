from odoo import models , fields , api , Command
from odoo.exceptions import ValidationError

class ProductDesign(models.Model):
    _name = 'product.design'
    
    name = fields.Char(string="Name",required=True)
    image = fields.Image("Image")
    default_code = fields.Char('Internal Reference',required=True)
    
    extra_price = fields.Float("Extra Price",related='product_attr_value_id.default_extra_price',readonly=False)
    product_attr_value_id = fields.Many2one('product.attribute.value')
    
    attr_value_ids = fields.One2many('product.attribute.value','product_design_id',"Attr Value Lines")
    product_ids = fields.Many2many('product.template',compute="_compute_product_ids",readonly=False,domain=[('sublimation_ok','=',True)])
    products_counter = fields.Integer("In Porducts",compute="_compute_product_ids")
    category_id = fields.Many2one('product.design.category',"Design")
    
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string="Attachments",
        compute='_compute_attachment_ids',
        store=True,
        readonly=False,
    )
    file_id = fields.Binary("File")
    def _compute_attachment_ids(self):
        for rec in self:
            rec.attachment_ids = self.env['ir.attachment'].search([
                ('res_model', '=', 'product.design'),
                ('res_id', '=', rec.id)
            ])
            
    def _compute_product_ids(self):
        for rec in self:
            products = self.env['product.template.attribute.value'].search([('product_attribute_value_id','in',rec.attr_value_ids.ids)]).attribute_line_id.product_tmpl_id
            rec.product_ids = [Command.link(product.id) for product in products]
            rec.products_counter = len(rec.product_ids)
    @api.model
    def get_data_for_product_template_view(self,*args,**kwargs):
        line_id = self.env['product.template.attribute.line'].browse(args).filtered_domain([('attribute_id.sublimation_ok','=',True)])
        line_id = line_id and line_id[0] or line_id
        value_ids = line_id.value_ids.filtered_domain([('without_design_ok','=',False)])
        return self.search_read(
            [('id','in',value_ids.product_design_id.ids)],
            ['id','name','default_code','extra_price'],
            limit=4,
            order='id desc',
        )
    
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
                'default_product_ids':[Command.link(kwargs.get('product_id'))],
                **kwargs
            } 
        }
    
    def _process_m2m(self,m2m):
        add = []
        sub = []
        if m2m:
            for command,value in m2m:
                if command == Command.LINK:
                    add.append(value)
                elif command == Command.UNLINK:
                    sub.append(value)
        return add , sub
    
            
    def write(self,vals):
        def __get_value_id(product_id):
            line_id =self.env['product.template'].browse(product_id).attribute_line_ids.filtered_domain([('attribute_id.sublimation_ok','=',True)])
            line_id = line_id and line_id[0] or line_id
            value_id =  self.env['product.attribute.value'].search([('product_design_id','=',self.id)]) 
            value_id = value_id and value_id[0] or value_id
            return line_id, value_id
        
        product_add, product_sub = self._process_m2m(vals.get('product_ids'))
        for product_id in product_add:
            line_id , value_id = __get_value_id(product_id)
            if line_id and value_id:
                line_id.value_ids = [Command.link(value_id.id)]
        for product_id in product_sub:
            line_id , value_id = __get_value_id(product_id)
            if line_id and value_id:
                line_id.value_ids = [Command.unlink(value_id.id)]
        res =  super().write(vals)
        if 'name' in vals:
            self.attr_value_ids.name = f"[{self.default_code}] {self.name}"
        return res
    
    def create(self,vals_list:dict):
        products , _ = self._process_m2m(vals_list.get('product_ids'))
        if products:
            attr_value = self.env['product.attribute.value'].create({
                'name': f"[{vals_list.get('default_code')}] {vals_list.get('name')}",
                'attribute_id': self.env.ref('e_sublimation.default_attr_design').id,
                'default_extra_price':vals_list.get('extra_price')
            })
            
            for product_id in products:
                line_id =self.env['product.template'].browse(product_id).attribute_line_ids.filtered_domain([('attribute_id.sublimation_ok','=',True)])
                line_id = len(line_id) > 1 and line_id[0] or line_id
                if not line_id:
                    raise ValidationError(f"No Sublimation Design Line in product: {product_id}")
                line_id.value_ids = [Command.link(attr_value.id)]
            record =  super().create(vals_list)
                
            attr_value.product_design_id = record.id
            return record
        return  super().create(vals_list)
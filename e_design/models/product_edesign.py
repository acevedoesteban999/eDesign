from odoo import models , fields , api , Command
from odoo.exceptions import ValidationError
from ..utils.utils import get_datas_m2m

class ProductEDesign(models.Model):
    _name = 'product.edesign'
    
    name = fields.Char(string="Name",required=True)
    image = fields.Image("Image")
    default_code = fields.Char('Internal Reference',required=True)
    
    # extra_price = fields.Float("Extra Price")
    # product_attr_value_id = fields.Many2one('product.attribute.value')
    
    # attr_value_ids = fields.One2many('product.attribute.value','product_design_id',"Attr Value Lines")
    # product_ids = fields.Many2many('product.template',domain=[('design_ok','=',True)],string="Products")
    # products_counter = fields.Integer("In Porducts",compute="_compute_product_ids")
    category_id = fields.Many2one('product.edesign.category',"Category")
    
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string="Attachments",
        store=True,
        readonly=False,
    )
    file_id = fields.Binary("File")
            
    # @api.depends('attr_value_ids')       
    # def _compute_product_ids(self):
    #     for rec in self:
    #         products = self.env['product.template.attribute.value'].search([('product_attribute_value_id','in',rec.attr_value_ids.ids)]).attribute_line_id.product_tmpl_id
    #         rec.product_ids = [Command.clear()] + [Command.link(product.id) for product in products]
    #         rec.products_counter = len(rec.product_ids)
        
    
    
    def _get_base_design_action(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Crete Design',   
            'res_model': 'product.edesign',   
            'view_type': 'form',    
            'view_mode': 'form',   
            'res_id': False,
            
            'target': 'new',
            'domain':[], 
            'context':{},
        }
    
    @api.model
    def get_design_action(self,method,context):
        if method == 'create':
            return {
                **self._get_base_design_action(),
                'views':[(self.env.ref('e_design.product_design_view_form').id,'form')],
                'context':context
            }
        elif method == 'open':
            return {
                **self._get_base_design_action(),
                'views':[(self.env.ref('e_design.product_design_view_form').id,'form')],
                'res_id': context.get('product_design_id'),
            }
        elif method == 'link':
            return{
                **self._get_base_design_action(),
                'res_model': 'e_design.product_design_attach_widget',   
                'views':[(self.env.ref('e_design.product_design_attach_view_form').id,'form')],
                'context': context
            } 
        # elif method == 'unlink':
        #     return{
        #         **self._get_base_design_action(),
        #         'res_model': 'e_design.product_design_unlink_widget',   
        #         'views':[(self.env.ref('e_design.product_design_unlink_view_form').id,'form')],
        #         'context': context
        #     } 
            
       
    def create(self,vals_list:dict):
        rec = super().create(vals_list)
        if product_id := self.env.context.get('default_product_id'):
            self.env['product.template'].browse(product_id).design_ids = [Command.link(rec.id)]
        return rec
    
    # def get_formview_action(self, access_uid=None):
    #     view_id = self.sudo().get_formview_id(access_uid=access_uid)
        
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': self._name,
    #         'views': [(view_id, 'form')],
    #         'target': self._context.get('action_target') or 'current' ,
    #         'res_id': self.id,
    #         'context': dict(self._context),
    #     }
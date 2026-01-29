from odoo import models , fields , api , Command
from odoo.exceptions import ValidationError
from ..utils.utils import get_datas_m2m

class ProductEDesign(models.Model):
    _name = 'product.edesign'
    
    name = fields.Char(string="Name",required=True)
    image = fields.Image("Image")
    default_code = fields.Char('Internal Reference',required=True)
    
    category_id = fields.Many2one('product.edesign.category',"Category")
    
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string="Attachments",
        store=True,
        readonly=False,
    )
    
    file_id = fields.Binary("File")
        
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
            
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"[{rec.default_code}] {rec.name}"

    
    
    def create(self,vals_list:dict):
        rec = super().create(vals_list)
        if product_id := self.env.context.get('default_product_id'):
            self.env['product.template'].browse(product_id).design_ids = [Command.link(rec.id)]
        return rec
    
    
    #OPEN ACTION IN 'NEW' TARGET
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
    
   
    
        
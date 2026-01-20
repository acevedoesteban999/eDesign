from odoo import models, fields, api , _ , Command

class ProductDesginUnlink(models.TransientModel):
    _name = 'e_design.product_design_unlink_widget'
    
    product_id = fields.Many2one('product.template',required=True,readonly=True)
    design_id = fields.Many2one('product.edesign',required=True,radonly=True)
    text = fields.Char(compute="_compute_text")
    
    @api.depends('product_id','design_id')
    def _compute_text(self):
        self.text = _("Are you sure you wana unlink design '%s' to product '%s'" % (self.design_id.name , self.product_id.name))
    
    def unlink_design(self):
        self.design_id.product_ids = [Command.unlink(self.product_id.id)]
        return {'type': 'ir.actions.act_window_close'}
        
    

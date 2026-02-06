from odoo import models, fields, api, _ , Command

class ProductDesginAttach(models.TransientModel):
    _name = 'e_design.product_design_attach_widget'
    _description = "Design Attach Widget"
    
    product_id = fields.Many2one('product.template',required=True,readonly=True)
    product_design_ids = fields.Many2many(related='product_id.design_ids')
    
    
    design_ids = fields.Many2many('product.edesign',required=True)
    
    def attach_design(self):
        self.ensure_one()
        self.product_id.design_ids = [Command.link(design.id) for design in self.design_ids]
        return {'type': 'ir.actions.act_window_close'}
        
    

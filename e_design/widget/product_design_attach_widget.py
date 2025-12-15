from odoo import models, fields, api, _ , Command

class ProductDesginAttach(models.TransientModel):
    _name = 'e_design.product_design_attach_widget'
    
    product_id = fields.Many2one('product.template',required=True,readonly=True)
    domain = fields.Char(compute="_compute_domain")
    design_id = fields.Many2one('product.design',required=True)
    
    @api.depends('product_id')
    def _compute_domain(self):
        for rec in self:
            rec.domain = str([('product_ids','not in',rec.product_id.ids)] if rec.product_id else [])

    def attach_design(self):
        self.ensure_one()
        self.design_id.product_ids = [Command.link(self.product_id.id)]
        return {'type': 'ir.actions.act_window_close'}
        
    

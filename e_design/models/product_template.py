from odoo import fields,models,api , Command , _
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    design_ok = fields.Boolean(string='Design')
    
    design_counter = fields.Integer("Designs Counter",compute="_compute_design_counter")
    design_ids = fields.Many2many(
        'product.edesign',
        string="Designs for Product Template",
    )
    
    def action_view_designs(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Designs',   
            'res_model': 'product.edesign',   
            'view_type': 'form',    
            'view_mode': 'kanban,list,form',   
            'views':[(False,'kanban'),(False,'list'),(False,'form')],
            'target': 'current',
            'domain':[('id',"in",self.design_ids.ids)],
            'context':{
                'create': False,
            } 
        }
    
    @api.depends('design_ids')
    def _compute_design_counter(self):
        for rec in self:
            rec.design_counter = len(rec.design_ids)

    @api.model
    def unlink_design(self, product_id ,design_id):
        self.browse(product_id).write({'design_ids': [Command.unlink(design_id)]})
        
        
        
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    
    def action_view_designs(self):
        return self.product_tmpl_id.action_view_designs()
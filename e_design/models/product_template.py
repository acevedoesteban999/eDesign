from odoo import fields,models,api , Command , _
class ProductProduct(models.Model):
    _inherit = 'product.template'

    design_ok = fields.Boolean(string='Design')
    
    design_counter = fields.Integer("Designs",compute="_compute_design_ids")
    design_ids = fields.Many2many(
        'product.design',
        string="Designs linked to Product Template",
        compute="_compute_design_ids",
    )
    
    def action_view_designs(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Designs',   
            'res_model': 'product.design',   
            'view_type': 'form',    
            'view_mode': 'kanban,list,form',   
            'views':[(False,'kanban'),(False,'list'),(False,'form')],
            'target': 'current',
            'domain':[('id',"in",self.attribute_line_ids.filtered_domain([('attribute_id.design_ok','=',True)]).value_ids.product_design_id.ids)],
            'context':{
                'create': False,
            } 
        }
    
    @api.depends('attribute_line_ids.value_ids')
    def _compute_design_ids(self):
        for rec in self:
            if rec.design_ok:
                rec.design_ids = [Command.link(design.id) for design in rec.attribute_line_ids.filtered_domain([('attribute_id.design_ok','=',True)]).value_ids.product_design_id]
                rec.design_counter = len(rec.design_ids)
            else:
                rec.design_ids = []
                rec.design_counter = 0
                
    @api.constrains('design_ok')
    def _check_design_ok(self):
        for rec in self:
            if rec.design_ok:
                attr = self.env.ref('e_design.default_attr_design')
                if attr.id not in rec.attribute_line_ids.attribute_id.ids:
                    rec.attribute_line_ids.create({
                        'attribute_id': attr.id,
                        'product_tmpl_id':self.id,
                        'value_ids': [Command.link(self.env.ref('e_design.default_attr_value_no_design').id)]
                    })
                    rec._create_variant_ids()
                    
    
        
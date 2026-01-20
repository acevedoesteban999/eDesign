from odoo import fields,models,api , Command , _
class ProductProduct(models.Model):
    _inherit = 'product.template'

    design_ok = fields.Boolean(string='Design')
    
    design_counter = fields.Integer("Designs",compute="_compute_design_counter")
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
    def get_designs_for_product_template_view(self,product_template):
        return self.env['product.edesign'].browse(product_template).read(['id','name','default_code','extra_price'])
    
    # @api.constrains('design_ok')
    # def _check_design_ok(self):
    #     for rec in self:
    #         if rec.design_ok:
    #             attr = self.env.ref('e_design.default_attr_design')
    #             if attr.id not in rec.attribute_line_ids.attribute_id.ids:
    #                 rec.attribute_line_ids.create({
    #                     'attribute_id': attr.id,
    #                     'product_tmpl_id':self.id,
    #                     'value_ids': [Command.link(self.env.ref('e_design.default_attr_value_no_design').id)]
    #                 })
    #                 rec._create_variant_ids()
                    
    
        
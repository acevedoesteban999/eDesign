# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class E_sublimationCategory(models.Model):
    _name = 'e_sublimation.category'
    _description = 'E_sublimationCategory'

    name = fields.Char('Name')
    image = fields.Image("Image")
    description = fields.Text("Description")
    child_ids = fields.One2many('product.template','category_sublimation_id','Childs')
    child_count = fields.Integer(compute="_compute_child_count")
    
    @api.depends('child_ids')
    def _compute_child_count(self):
        for rec in self:
            rec.child_count = len(rec.child_ids)
            
    def action_open_product_childs_category(self):
        return {
            'name': f'{self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'kanban,list,form',
            'target': 'current',
            'domain': [('category_sublimation_id','=',self.id)],
            'context': {'default_category_sublimation_id': self.id},
            'views': [
                (self.env.ref('e_sublimation.product_childs_view_kanban_sublimation').id,'kanban'),
                (self.env.ref('e_sublimation.product_childs_view_list_sublimation').id,'list'),
                (self.env.ref('product.product_template_only_form_view').id,'form'),  
            ],
        }
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ePosMrpCreataOrderWizard(models.TransientModel):
    _name = 'e_pos_mrp.creata_order_wizard'
    _description = "Create MRP in POS Wizadrd"

    product_tmpl_id = fields.Many2one(related='product_id.product_tmpl_id')
    product_id = fields.Many2one('product.product',"Product")
    product_qty = fields.Integer("Qty",default=1)
    bom_id = fields.Many2one('mrp.bom','Bom Material')
    # material_ids = fields.One2many(related='bom_id.bom_line_ids')
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                rec.bom_id = rec.bom_id.search([('product_id','=',rec.product_id.id)]) or rec.bom_id.search([('product_tmpl_id','=',rec.product_tmpl_id.id)])
            
    def crateManufacture(self):
        self.env['mrp.production'].create({
            'product_qty': self.product_qty,
            'product_id': self.product_id.id,
            'bom_id': self.bom_id.id
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _("MRP Production Created"),
                'type': 'success',
                'sticky': False,
                'next':{
                    'type': 'ir.actions.act_window_close'
                }
                    
            }
        }
        
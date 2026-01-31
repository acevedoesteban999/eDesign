# -*- coding: utf-8 -*-
from odoo import models, fields, api, _ , exceptions

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    dinamic_mto_ok = fields.Boolean(string='Dinamic MTO',help="Configure Replenish on Order (MTO) with dinamic bill of material. Require MTO route",compute="_compute_mto_dinamic",store=True,default=False)
    lines_dinamic_bill_material_ids = fields.One2many('product.diamic.mto.line',"parent_product_template_id",name="Lines of Dinamic Bill Materials")
    
    currency_symbol = fields.Char(related='currency_id.symbol')
    currency_position = fields.Selection(related='currency_id.position')
    
    @api.depends('mto_ok')
    def _compute_mto_dinamic(self):
        for rec in self:
            dinamic_mto_ok = False
            if rec.mto_ok:
                dinamic_mto_ok = rec.dinamic_mto_ok
            rec.dinamic_mto_ok = dinamic_mto_ok
                
    
    @api.constrains('dinamic_mto_ok','lines_dinamic_bill_material_ids')
    def check_dinamic_mto_ok(self):
        for rec in self:
            if rec.dinamic_mto_ok and not rec.lines_dinamic_bill_material_ids:
                raise exceptions.UserError(_("Dinamic MTO Requiere a Dinamic Bill of Materials"))
            
        
    @api.model
    def get_dinamic_final_price(self):
        self.ensure_one()
        return sum(self.lines_dinamic_bill_material_ids.lst_price)
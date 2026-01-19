# -*- coding: utf-8 -*-
from odoo import models, fields



class PosCategory(models.Model):
    _inherit = 'pos.category'

    show_pos_outofstock = fields.Boolean("Show products in POS with outofstock")
    
    def get_show_pos_outofstock_recursive(self):
        if self:
            return any(self.mapped('show_pos_outofstock')) or (self.parent_id.get_show_pos_outofstock_recursive() if self.parent_id else False)
        return False
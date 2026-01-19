# -*- coding: utf-8 -*-

from odoo import fields, models , api

class PosConfig(models.Model):
    _inherit = 'pos.config'

    hide_out_stock = fields.Boolean(
        string="Hide Out of Stock",
        help="If check, products out of stock will be hidden from the POS"
    )
    
    
    
    




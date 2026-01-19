# -*- coding: utf-8 -*-

from odoo import fields, models , api

class PosConfig(models.Model):
    _inherit = 'pos.config'

    show_mrp_delivery = fields.Boolean(
        string="Show in POS Delivery Info",
        help="If checked , is activated the delivery action , confirm and view for pickings"
    )
    
    
    
    




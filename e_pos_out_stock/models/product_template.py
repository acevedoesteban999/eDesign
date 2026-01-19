# -*- coding: utf-8 -*-
from odoo import models, fields



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    show_pos_outofstock = fields.Boolean("Show products in POS with Out of Stock")
    

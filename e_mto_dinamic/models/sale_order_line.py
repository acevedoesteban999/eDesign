# -*- coding: utf-8 -*-
from odoo import models, fields, api, _ , exceptions

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_dinamic_mto = fields.Boolean(related="product_template_id.dinamic_mto_ok")
    dinamic_bill_material_data = fields.Json()
            
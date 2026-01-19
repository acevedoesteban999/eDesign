# -*- coding: utf-8 -*-
from odoo import models, fields, api, _ , exceptions

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_dinamic_mto = fields.Boolean(related="product_template_id.dinamic_mto_ok")
    dinamic_bill_material_data = fields.Json()
    
    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        super()._action_launch_stock_rule(previous_product_uom_qty)
            
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    has_generic_product = fields.Boolean(related='product_template_id.generic_ok')
    generic_bill_material_data = fields.Json()
    
    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        lines = self.filtered_domain([('has_generic_product','=',False)])
        if lines:
            super(SaleOrderLine,lines)._action_launch_stock_rule(previous_product_uom_qty)
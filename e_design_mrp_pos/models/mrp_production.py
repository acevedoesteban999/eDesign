# -*- coding: utf-8 -*-
from odoo import models,fields,api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    def _check_design_routes(self):
        if self.pos_order_line_id:
            self.design_id = self.pos_order_line_id.design_id.id
        else:
            return super()._check_design_routes()
    
from odoo import _, api, fields, models


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    design_id = fields.Many2one('product.edesign',"Design")

    @api.model
    def _load_pos_data_fields(self, config_id):
        data = super()._load_pos_data_fields( config_id)
        return data + ['design_id']
    
    
   
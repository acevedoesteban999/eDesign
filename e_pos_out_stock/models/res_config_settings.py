from odoo import fields, models 

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_hide_out_stock = fields.Boolean(
        related="pos_config_id.hide_out_stock",
        readonly=False,
        implied_group='e_pos_out_stock.group_hide_out_stock',
    )
    


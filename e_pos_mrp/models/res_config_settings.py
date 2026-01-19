from odoo import fields, models 

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    show_mrp_delivery = fields.Boolean(
        related="pos_config_id.show_mrp_delivery",
        readonly=False,
    )
    


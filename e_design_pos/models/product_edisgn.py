from odoo import models , api

class ProducteDesign(models.Model):
    _name = "product.edesign"
    _inherit = ['product.edesign','mail.thread', 'mail.activity.mixin', "pos.bus.mixin", 'pos.load.mixin']


    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['name','default_code','image']
    
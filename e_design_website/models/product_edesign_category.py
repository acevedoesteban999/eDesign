from odoo import models , fields , api

class ProductEDesign(models.Model):
    _inherit = "product.edesign.category"
    
    is_published = fields.Boolean("Is Published",help="Is Published on Website",default=True)
    subcategories_ids = fields.One2many('product.edesign.category','parent_id',"Sub-Categories")
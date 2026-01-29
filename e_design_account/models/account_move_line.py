from odoo import models, fields, api, _

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    _description = 'AccountMove eDesign'

    design_id = fields.Many2one('product.edesign',"Design")
    parent_design_ids = fields.Many2many(related='product_id.product_tmpl_id.design_ids')
    
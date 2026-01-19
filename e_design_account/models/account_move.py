from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'AccountMove'

    has_design = fields.Boolean(compute='_compute_has_design')
    
    @api.depends('line_ids')
    def _compute_has_design(self):
        for rec in self:
            rec.has_design = any(rec.line_ids.mapped('design_id'))
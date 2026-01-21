from odoo import _, api, fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    has_design = fields.Boolean(compute='_compute_has_design')
    
    @api.depends('lines')
    def _compute_has_design(self):
        for rec in self:
            rec.has_design = any(rec.lines.mapped('design_id'))
    
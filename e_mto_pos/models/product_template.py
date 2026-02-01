# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    can_create_mto_pos = fields.Boolean(
        string='Manufacture on demand',
        help="Product should make mrp order in pos. Requires MTO route",
        conmpute="_compute_can_create_mto_pos",
        store=True,
        readonly=False,
        )
    
    @api.depends('mto_ok')
    def _compute_can_create_mto_pos(self):
        for rec in self:
            mto_ok = False
            if rec.mto_ok:
                mto_ok = rec.mto_ok
            rec.mto_ok = mto_ok
# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductDesignCategory(models.Model):
    _name = 'product.edesign.category'
    _description = 'ProductEDesignCategory'

    name = fields.Char('Name')
    image = fields.Image("Image")
    parent_id = fields.Many2one('product.edesign.category')
    design_ids = fields.One2many('product.edesign','category_id',"Designs")
    design_counter = fields.Integer("Designs",compute="_compute_design_counter")
    
    @api.depends('design_ids')
    def _compute_design_counter(self):
        for rec in self:
            rec.design_counter = len(rec.design_ids)
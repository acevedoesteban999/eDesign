# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductDesignCategory(models.Model):
    _name = 'product.design.category'
    _description = 'ProductDesignCategory'

    name = fields.Char('Name')
    image = fields.Image("Image")
    design_ids = fields.One2many('product.design','category_id',"Designs")
    design_counter = fields.Integer("Designs",compute="_compute_design_counter")
    
    @api.depends('design_ids')
    def _compute_design_counter(self):
        for rec in self:
            rec.design_counter = len(rec.design_ids)
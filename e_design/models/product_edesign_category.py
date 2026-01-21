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
    
    def _get_display_name (self):
        return (self.parent_id._get_display_name() + " / " + self.name ) if self.parent_id else self.name
    
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec._get_display_name()
            
            
    @api.depends('design_ids')
    def _compute_design_counter(self):
        for rec in self:
            rec.design_counter = len(rec.design_ids)
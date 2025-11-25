# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductDesignCategory(models.Model):
    _name = 'product.design.category'
    _description = 'ProductDesignCategory'

    name = fields.Char('Name')
    design_ids = fields.One2many('product.design','category_id',"Designs")
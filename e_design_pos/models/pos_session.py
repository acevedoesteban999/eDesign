# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import defaultdict
from datetime import timedelta
from itertools import groupby, starmap
from markupsafe import Markup

from odoo import api, fields, models, _, Command
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, convert, plaintext2html
from odoo.service.common import exp_version
from odoo.osv.expression import AND


class PosSession(models.Model):
    _inherit = 'pos.session'

    
    @api.model
    def _load_pos_data_models(self, config_id):
        data = super()._load_pos_data_models(config_id)
        return data + ['product.edesign']
    

    
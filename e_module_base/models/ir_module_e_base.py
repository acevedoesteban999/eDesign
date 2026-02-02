# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ , modules , Command
from odoo.exceptions import ValidationError
from odoo.addons.base.models.ir_module import STATES

class EGitModuleBase(models.AbstractModel):
    _name = 'ir.module.e_base'
    _description = 'Base Module'
    _rec_name = 'module_name'

    module_id = fields.Many2one('ir.module.module','Module',required=True,ondelete="cascade")
    module_name = fields.Char("Module Technical Name",related='module_id.name')
    module_icon = fields.Char(compute="_compute_module_icon")
    local_path = fields.Char(compute="_compute_local_path")
    module_state = fields.Selection(related='module_id.state')
    
    state = fields.Selection([
        ('error','Error'),
    ],compute="_compute_state",store=True)
    
    
    installed_version = fields.Char("Installed Version",related='module_id.latest_version')
    local_version = fields.Char("Local Version",related='module_id.installed_version')
    
    error_msg = fields.Char("Error")
    last_check = fields.Datetime(default=fields.Datetime.now,readonly=True)
    
    # ===================================================================
    # API
    # ===================================================================
    
    @api.depends('module_id')
    def _compute_state(self):
        for rec in self:
            rec.state = rec.state or False
    
    @api.constrains('module_id')
    def _check_unique_module(self):
        for rec in self:
            if self.search([
                ('module_id', '=', rec.module_id.id),
                ('id', '!=', rec.id)
            ]):
                raise ValidationError("Module must be unique!")
    
    @api.depends('module_id')
    def _compute_local_path(self):
        for rec in self:
            if rec.module_id:
                rec.local_path = modules.get_module_path(rec.module_name)
            else:
                rec.local_path = False
    
    @api.onchange('module_id')
    def _compute_module_icon(self):
        for rec in self:
            rec.module_icon = f"/{rec.module_name}/static/description/icon.png"
            
    def install_module(self):
        self.module_id.button_immediate_install()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
        
        
    def action_recompute_data(self):
        self._compute_state()
        
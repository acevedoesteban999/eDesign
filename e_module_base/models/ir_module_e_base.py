# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ , modules , Command


class EGitModuleBase(models.AbstractModel):
    _name = 'ir.module.e_base'
    _description = 'Base Module'
    _rec_name = 'module_name'

    module_name = fields.Char("Module Technical Name", required=True)
    module_icon = fields.Char(compute="_compute_module_icon")
    module_exist = fields.Boolean("Module Exist",compute="_compute_module_exist")
    module_installed = fields.Boolean("Module Installed",compute="_compute_module_installed")
    local_path = fields.Char(compute="_compute_local_path")
    module_status = fields.Selection([
        ('ready','Ready'),
        ('no_installed','No Installed'),
        ('dont_found','Dont Found'),
    ],compute="_compute_module_status",readonly=True)
    
    installed_version = fields.Char("Installed Version", compute="_compute_installed_versions",
                                    help="Version installed on Database")
    
    _sql_constraints = [
        ('unique_module', 'unique(module_name)', 'Module must be unique!')
    ]
    
    error_msg = fields.Char("Error")
    last_check = fields.Datetime(default=fields.Datetime.now,readonly=True)
    
    # ===================================================================
    # API
    # ===================================================================

    @api.depends('module_name')
    def _compute_installed_versions(self):
        for rec in self:
            rec.installed_version = self.env['ir.module.module'].search([('name','=',rec.module_name)]).latest_version
    
    @api.depends('module_name')
    def _compute_local_path(self):
        for rec in self:
            if rec.module_name:
                rec.local_path = modules.get_module_path(rec.module_name)
            else:
                rec.local_path = False
    
    @api.depends('module_name')
    def _compute_module_exist(self):
        for rec in self:
            rec.module_exist = bool(rec.module_name) and  rec.env['ir.module.module'].search_count([('name','=',rec.module_name)]) != 0 and bool(rec.local_path)
    
    @api.depends('module_name')
    def _compute_module_installed(self):
        for rec in self:
            rec.module_installed = bool(rec.module_exist) and  bool(rec.env['ir.module.module'].search([('name','=',rec.module_name)]).latest_version)
    
    @api.depends('module_name')
    def _compute_module_status(self):
        for rec in self:
            rec.module_status = 'ready' if rec.module_installed else 'no_installed' if rec.module_exist else 'dont_found'
    
    @api.onchange('module_name')
    def _compute_module_icon(self):
        for rec in self:
            rec.module_icon = f"/{rec.module_name}/static/description/icon.png"
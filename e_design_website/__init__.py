# -*- coding: utf-8 -*-
from . import models
from . import controllers


from odoo import _

def _install_designs_menu_and_page(env):
    try:
        menu = env['website.menu'].search([('url','=','/edesigns')])
        if not menu:
            env['website.menu'].create({
                'name': _('Designs'),
                'url': '/edesigns',
            })
    except:
        pass

def _uninstall_designs_menu_and_page(env):
    try:
        menu = env['website.menu'].search([
            ('url', '=', '/edesigns'),
        ])
        if menu:
            menu.unlink()


    except Exception:
        pass
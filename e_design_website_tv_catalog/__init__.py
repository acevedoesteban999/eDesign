# -*- coding: utf-8 -*-
from . import controllers

from odoo import _

def _install_tv_catalog_menu_and_page(env):
    try:
        menu = env['website.menu'].search([('url','=','/tv/catalog')])
        if not menu:
            env['website.menu'].create({
                'name': _('TV Catalog'),
                'url': '/tv/catalog',
            })
    except:
        pass

def _uninstall_tv_catalog_menu_and_page(env):
    try:
        menu = env['website.menu'].search([
            ('url', '=', '/tv/catalog'),
        ])
        if menu:
            menu.unlink()


    except Exception:
        pass
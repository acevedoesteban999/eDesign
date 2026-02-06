import logging
from odoo import api, SUPERUSER_ID
from odoo.tools.sql import  rename_column , column_exists

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    
    _logger.info("Starting ePosOutStock migration: 18.0.1.0.0")
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    view = env.ref('e_pos_out_stock.e_pos_out_stock_res_config_settings_view_form_pos_invoice_toggle', 
                   raise_if_not_found=False)
    if view:
        _logger.info(f"Deleting view: ID={view.id}, Name={view.name}")
        view.unlink()
    else:
        _logger.info("View not found")
    
    if column_exists(cr,'pos_category','show_pos_outofstock'):
        rename_column(cr,'pos_category','show_pos_outofstock','show_pos_outstock')
    if column_exists(cr,'product_template','show_pos_outofstock'):
        rename_column(cr,'product_template','show_pos_outofstock','show_pos_outstock')
    
    
    env['ir.model'].invalidate_model()
    
    _logger.info("Migration Finished")
    
    
    
    
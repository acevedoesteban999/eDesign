import logging
from odoo.tools.sql import table_exists 
_logger = logging.getLogger(__name__)


def post_install_hook(env):
    _logger.info("Starting e_mto_pos installation")
    cr = env.cr
    
    if not table_exists(cr, 'z_temp_pos_mrp_data'):
        _logger.info("No temporary table from e_pos_mrp found, nothing to migrate")
        return
    
    _logger.info("Found temporary table z_temp_pos_mrp_data")
    
    
    cr.execute("""
        UPDATE product_template pt
        SET can_create_mto_pos = t.can_create_pos_mrp
        FROM public.z_temp_pos_mrp_data t
        WHERE pt.id = t.product_template_id
          AND t.can_create_pos_mrp IS NOT NULL
    """)
    
    cr.execute("DROP TABLE public.z_temp_pos_mrp_data")
    
    _logger.info("Temporary table dropped, migration completed")
    
    env['product.template'].invalidate_model(['can_create_mto_pos'])
    env['product.product'].invalidate_model(['has_create_mto_pos'])  
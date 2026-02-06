# e_pos_mrp/migrations/18.0.2.0.0/pre-migrate.py
import logging
from odoo import api, SUPERUSER_ID
_logger = logging.getLogger(__name__)

XML_IDS = [
    "e_pos_mrp.pos_order_form_inherit_pos_order_form",
    "e_pos_mrp.product_template_form_view",
    "e_pos_mrp.pos_order_form_inherit_mrp_production_form",
    "e_pos_mrp.e_pos_out_stock_res_config_settings_view_form_pos_invoice_toggle",
]


def migrate(cr, version):
    if not version:
        return
    _logger.info("Starting e_pos_mrp migration")
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    for xml_id in XML_IDS:
        view = env.ref(xml_id, 
                   raise_if_not_found=False)
        if view:
            _logger.info(f"Deleting view: ID={view.id}, Name={view.name}")
            view.unlink()
        else:
            _logger.info(f"View not found: {xml_id}")
    
    e_mto_pos = env['ir.module.module'].search([
        ('name', '=', 'e_mto_pos'),
        ('state', '=', 'installed')
    ], limit=1)
    
    if e_mto_pos:
        _logger.info("e_mto_pos is installed, migrating directly")
        
        cr.execute("""
            UPDATE product_template pt
            SET can_create_mto_pos = t.can_create_pos_mrp
            FROM public.z_temp_pos_mrp_data t
            WHERE pt.id = t.product_template_id
            AND t.can_create_pos_mrp IS NOT NULL
        """)
        
        _logger.info("Migrated %s records directly to e_mto_pos", cr.rowcount)
        
        return
    
    _logger.warning("e_mto_pos is not installed, creating temporary table")
    
    cr.execute("""
        CREATE TABLE IF NOT EXISTS public.z_temp_pos_mrp_data (
            id SERIAL PRIMARY KEY,
            product_template_id INTEGER NOT NULL,
            can_create_pos_mrp BOOLEAN,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(product_template_id)
        )
    """)
    
    cr.execute("TRUNCATE public.z_temp_pos_mrp_data")
    
    cr.execute("""
        INSERT INTO public.z_temp_pos_mrp_data 
            (product_template_id, can_create_pos_mrp)
        SELECT 
            id,
            can_create_pos_mrp
        FROM product_template
        WHERE can_create_pos_mrp IS NOT NULL
        ON CONFLICT (product_template_id) DO UPDATE
        SET can_create_pos_mrp = EXCLUDED.can_create_pos_mrp
    """)
    
    _logger.info("Temporary table z_temp_pos_mrp_data created and populated, waiting for e_mto_pos")
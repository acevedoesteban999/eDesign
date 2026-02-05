# e_pos_mrp/migrations/18.0.2.0.0/pre-migrate.py
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    _logger.info("Starting e_pos_mrp migration")
    
    e_mto_pos = env['ir.module.module'].search([
        ('name', '=', 'e_mto_pos'),
        ('state', '=', 'installed')
    ], limit=1)
    
    if e_mto_pos:
        _logger.info("e_mto_pos is installed, migrating directly")
        
        cr.execute("""
            UPDATE product_template pt
            SET can_create_mto_pos = 
                COALESCE(
                    (SELECT can_create_pos_mrp 
                     FROM product_template pt2 
                     WHERE pt2.id = pt.id),
                    FALSE
                )
            WHERE EXISTS (
                SELECT 1 FROM product_template pt3 
                WHERE pt3.id = pt.id 
                AND pt3.can_create_pos_mrp IS NOT NULL
            )
        """)
        
        actualizados = cr.rowcount
        _logger.info("Migrated %s records directly to e_mto_pos", actualizados)
        
        cr.execute("""
            SELECT COUNT(*) FROM product_template 
            WHERE can_create_mto_pos = TRUE
        """)
        total_mto = cr.fetchone()[0]
        _logger.info("Total records in e_mto_pos with can_create_mto_pos=TRUE: %s", total_mto)
        
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
    
    guardados = cr.rowcount
    _logger.info("Saved %s records to temporary table", guardados)
    _logger.info("Temporary table z_temp_pos_mrp_data created and populated, waiting for e_mto_pos")
from odoo import models , api 
from odoo.osv.expression import AND
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    
    @api.model
    def read_assigned_picking_ids(self, domain, limit, offset):
        _domain = [('state', 'not in', ['draft','cancel']),('pos_order_id','!=',False)]
        if domain:
            _domain = AND([domain, _domain])
            
        pickings_info = self.search(
            _domain, 
            limit=limit, 
            offset=offset, 
            order='create_date desc'
            ).read([
                'id',
                'name',
                'create_date',
                'scheduled_date',
                'state',
                'pos_order_id',
                'partner_id'
            ]
        )
            
        totalPickingCount = self.search_count(_domain)
        return {
            'PickingsInfo': pickings_info, 
            'totalPickingCount': totalPickingCount}
        
    @api.model
    def read_picking_lines(self,picking_id):
        return self.env['stock.picking'].browse(picking_id).move_ids_without_package.read([
                'product_id',
                'quantity',
        ])
        
    @api.model
    def confirm_picking(self,picking_id):
        self.env['stock.picking'].browse(picking_id).button_validate()
    
    
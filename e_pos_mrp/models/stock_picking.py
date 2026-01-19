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
                'product_uom_qty',
        ])
        
    @api.model
    def confirm_picking(self,picking_id):
        self.env['stock.picking'].browse(picking_id).button_validate()
    
    
    @api.model
    def read_picking_by_pos_order(self,pos_order_id):
        order = self.env['pos.order'].browse(pos_order_id)
        has_picking = any(map(lambda p: p == 'waiting',order.picking_ids.mapped('state')))
        if has_picking:
            return {
                'picking_id':order.picking_ids and order.picking_ids.filtered_domain([('state','=','waiting')]).read(['name'])[0],
                'mrp_production_count': order.mrp_production_count
            }
        return False
    
from odoo import models , api  , fields
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    
    pos_order_pos_reference = fields.Char(related='pos_order_id.pos_reference')
    pos_order_tracking_number = fields.Char(related='pos_order_id.tracking_number')
    pos_order_general_note = fields.Text(related='pos_order_id.general_note')
    mrp_pos_ok = fields.Boolean(default=False)
    
    
    @api.model
    def confirm_picking(self,picking_id):
        self.env['stock.picking'].browse(picking_id).button_validate()
    
    
    @api.model
    def read_picking_by_pos_order(self,pos_order_id):
        order = self.env['pos.order'].browse(pos_order_id)
        mrp_pos_pikcing = order.picking_ids.filtered_domain([('mrp_pos_ok','=',True)])
        mrp_pos_pikcing = mrp_pos_pikcing and mrp_pos_pikcing[0]
        if mrp_pos_pikcing:
            return {
                'pos_reference': order.pos_reference,
                'tracking_number': order.tracking_number,
                'picking_pos_mrp_name': order.picking_pos_mrp.name,
            }
        return False
    
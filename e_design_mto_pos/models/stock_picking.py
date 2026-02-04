from odoo import models , api  , fields
from odoo.osv.expression import AND
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    @api.model
    def read_picking_lines(self, picking_id):
        lines = super().read_picking_lines(picking_id)
        for line in lines:
            line = self.env['pos.order.line'].browse(line.get('id'))
            if line.design_id:
                line.update({
                    'design_id':{
                        'default_code': line.design_id.default_code or '',
                    }
                })
                
        return lines
        
    
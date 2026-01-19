from odoo import models , api , Command

class MrpProduction(models.Model):
    _inherit = "mrp.production"
    
    def _get_move_dest_line(self,move_finished_ids):
        for move in move_finished_ids:
            while move:
                if move.sale_line_id:
                    return move.sale_line_id
                move = move.move_dest_ids[:1]

    @api.model
    def create(self, values):
        rec = super().create(values)
        product = rec.product_id
        if product.product_tmpl_id.dinamic_mto_ok:
            moves = []    
            sale_order_line = self._get_move_dest_line(rec.move_dest_ids)
            if sale_order_line:
                for dinamic_bill in sale_order_line.dinamic_bill_material_data:
                    moves.append(
                        rec._get_move_raw_values(
                            self.env['product.product'].browse(dinamic_bill['product']['id']),
                            dinamic_bill['qty'],
                            sale_order_line.product_uom
                        ),
                    )
                    
                rec.move_raw_ids = [Command.create(move) for move in moves]
        
        return rec
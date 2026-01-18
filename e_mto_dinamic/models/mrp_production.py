from odoo import models

class MrpProduction(models.Model):
    _inherit = "mrp.production"
    
    def _get_moves_raw_values(self):
        moves = []
        for rec in self:
            if rec.product_tmpl_id.dinamic_mto_ok:
                for dinamic_bill in rec.product_tmpl_id.lines_dinamic_bill_material_ids:
                    moves.append(rec._get_move_raw_values(
                        dinamic_bill['product_id'],
                        dinamic_bill['qty'],
                        rec.product_id.uom_id.id,
                    ))
            else:
                moves += super(MrpProduction,rec)._get_moves_raw_values()
        return moves
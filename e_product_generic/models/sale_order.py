# -*- coding: utf-8 -*-
from odoo import models, fields, api, _ , Command
from odoo.exceptions import UserError
class SaleOrde(models.Model):
    _inherit = 'sale.order'
    
    
    def _action_confirm(self):
        if order_lines := self.order_line.filtered_domain([('has_generic_product','=',True)]):
            self._create_mrp_from_generic(order_lines)
        return super()._action_confirm()
    
    def _create_mrp_from_generic(self, lines):
        self.ensure_one()
        mrp_productions = self.env['mrp.production']
        group = self.procurement_group_id or self.env["procurement.group"].create({
            'name': self.name,
            'partner_id': self.partner_id.id,
            'move_type': 'one',
            'sale_id': self.id,
        }) 
        for line in lines:
            mrp_productions += self._create_mrp_production(line,group)
        self._create_picking_for_productions(mrp_productions,group)  
            
    def _create_mrp_production(self, line,group):
        product = line.product_id
    
        mrp_order = self.env['mrp.production'].create({
            'product_id': product.id,
            'product_qty': abs(line.product_uom_qty),
            'product_uom_id': product.uom_id.id,
            'origin': self.name,
            'sale_line_id': line.id,
            'state': 'confirmed',
            'procurement_group_id': group.id,   
        })
        moves = []
        for generic_bil in line.generic_bill_material_data:
            
            moves.append(
                mrp_order._get_move_raw_values(
                    line.product_id.browse(generic_bil.get('id')),
                    generic_bil.get('qty'),
                    line.product_id.uom_id
                ),
            )
            
        mrp_order.move_raw_ids =  [ Command.create(m) for m in moves]
        mrp_order.move_finished_ids =  [ Command.create(m) for m in mrp_order._get_moves_finished_values()]
        
        return mrp_order
      
    def _create_picking_for_productions(self, mrp_productions,group):
        self.ensure_one()
        picking_type = self.env['stock.picking.type'].browse(self.env['stock.picking'].with_context(restricted_picking_type_code='outgoing')._default_picking_type_id())
        location_id = picking_type.default_location_src_id
        location_dest_id = (
            self.partner_id.property_stock_customer
            or picking_type.default_location_dest_id
        )

        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': location_id.id,            
            'location_dest_id': location_dest_id.id,
            'partner_id': self.partner_id.id,
            'origin': self.name,
            'sale_id': self.id,
            'group_id': group.id,
            'move_type': 'one',
            'state': 'draft', 
        })
        for mrp_production in mrp_productions:
            move_sale = self.env['stock.move'].create({
                'name': mrp_production.product_id.display_name,
                'product_id': mrp_production.product_id.id,
                'product_uom_qty': abs(mrp_production.product_qty),
                'product_uom': mrp_production.product_id.uom_id.id,
                'picking_id': picking.id,
                'location_id': location_id.id,
                'location_dest_id': location_dest_id.id,
                'group_id': group.id,
                'procure_method': 'make_to_order',
                'origin': self.name,
                'state': 'waiting',
                'date': mrp_production.date_finished,
            })

            finished_moves = mrp_production.move_finished_ids.filtered(
                lambda m: m.product_id == mrp_production.product_id
            )
            move_sale.move_orig_ids = [Command.link(fm.id) for fm in finished_moves]
        return picking
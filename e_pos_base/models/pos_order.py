# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.osv.expression import AND

class PosOrder(models.Model):
    _inherit = 'pos.order'

    
    def get_read_no_draft_pos_order_ids_fields(self):
        return [
            'id',
            'name',
            'create_date',
            'state',
            'pos_reference',
            'tracking_number',
            'general_note',
            'partner_id',
        ]
    
    @api.model
    def read_no_draft_pos_order_ids(self, domain, limit, offset):
        _domain = [('state', 'not in', ['draft'])]
        if domain:
            _domain = AND([domain, _domain])
        _domain = domain
        data = self.search(
            _domain, 
            limit=limit, 
            offset=offset, 
            order='create_date desc'
            ).read(self.get_read_no_draft_pos_order_ids_fields())

        return {
            'data': data, 
            'totalCount': self.search_count(_domain)}
        
    @api.model
    def read_pos_order_lines(self, pos_order_id):
        pos_order = self.env['pos.order'].browse(pos_order_id) 
        
        result = []
        for line in  pos_order.lines:
            price_unit = line.price_unit
            product = line.product_id
            qty = line.qty
            discount = line.discount 
            
            result.append({
                'id': line.id,
                'productName': str(product.display_name),
                'price': str(round(price_unit * qty * (1 - discount/100), 2)) or '',
                'qty': str(qty),
                'unit': str(product.uom_id.name),
                'unitPrice': str(round(price_unit, 2)),
                'discount': str(discount) if discount > 0 else '0',
                'oldUnitPrice': str(round(price_unit, 2)) if discount > 0 else '',
                'price_without_discount': str(round(price_unit * qty, 2)) if discount > 0 else '',
                'customerNote': line.customer_note or '',
                'internalNote': line.note or '',
                'imageSrc': f'/web/image/product.product/{product.id}/image_128' if product.image_128 else '',
                'isSelected': False,
                'comboParent': '',
                'packLotLines': [],
                'taxGroupLabels': ''
            })
        return result
    
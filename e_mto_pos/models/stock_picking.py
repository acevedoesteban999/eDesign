from odoo import models , api  , fields
from odoo.osv.expression import AND
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    
    pos_order_pos_reference = fields.Char(related='pos_order_id.pos_reference')
    pos_order_tracking_number = fields.Char(related='pos_order_id.tracking_number')
    pos_order_general_note = fields.Text(related='pos_order_id.general_note')
    mrp_pos_ok = fields.Boolean(default=False)
    
    @api.model
    def read_assigned_picking_ids(self, domain, limit, offset):
        _domain = [('state', 'not in', ['draft']),('pos_order_id','!=',False)]
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
                'pos_order_pos_reference',
                'pos_order_tracking_number',
                'pos_order_general_note',
                'partner_id',
            ]
        )
        
        
         
        totalPickingCount = self.search_count(_domain)
        return {
            'PickingsInfo': pickings_info, 
            'totalPickingCount': totalPickingCount}
        
    @api.model
    def read_picking_lines(self, picking_id):
        picking = self.env['stock.picking'].browse(picking_id) 
        
        result = []
        for line in  picking.pos_order_id.lines:
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
                'has_create_mto_pos':product.has_create_mto_pos,
                'comboParent': '',
                'packLotLines': [],
                'taxGroupLabels': ''
            })
        return result
        
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
                'pos_order_pos_reference': mrp_pos_pikcing.pos_order_pos_reference,
                'pos_order_tracking_number': mrp_pos_pikcing.pos_order_tracking_number
            }
        return False
    
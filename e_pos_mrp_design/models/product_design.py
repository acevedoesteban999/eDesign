from odoo import models

class ProductDesign(models.Model):
    _inherit = 'product.design'
    
    def get_formview_action(self, access_uid=None):
        view_id = self.sudo().get_formview_id(access_uid=access_uid)
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'views': [(view_id, 'form')],
            'target': self._context.get('action_target') or 'current' ,
            'res_id': self.id,
            'context': dict(self._context),
        }
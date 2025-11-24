from odoo import models

class ProductDesign(models.Model):
    _inherit = 'product.design'
    
    def get_formview_action(self, access_uid=None):
        view_id = self.sudo().get_formview_id(access_uid=access_uid)
        if not view_id and (view_form := self._context.get('view_form')):
            view_id = self.sudo().env.ref(view_form,False)
            view_id = view_id and view_id.id or view_id
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'views': [(view_id, 'form')],
            'target': self._context.get('action_target') or 'current' ,
            'res_id': self.id,
            'context': dict(self._context),
        }
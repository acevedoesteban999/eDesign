from odoo import models , _
from odoo.exceptions import ValidationError
class ProductTemplateAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"
    
    
    def unlink(self):
        for rec in self:
            if rec.attribute_id.design_ok and rec.product_tmpl_id.design_ok:
                raise ValidationError(_("Can not delete Design Line with Design Product"))
        return super().unlink()
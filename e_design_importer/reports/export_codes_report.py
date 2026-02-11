from odoo import models , _

class ExportCodesXlsx(models.AbstractModel):
    _name = 'report.e_design_importer.export_codes_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Export Codes Excel Report'

    def generate_xlsx_report(self, workbook, data, objs):
        sheet1 = workbook.add_worksheet(_('Products'))
        sheet1.write_row(0, 0, ['id', _('name'), _('default_code')])
        sheet1.set_column(0, 2, 20)
        for row, obj in enumerate(self.env['product.template'].search([('design_ok','=',True)]), 1):
            sheet1.write_row(row, 0, [obj.id, obj.name, obj.default_code or ''])
        
        
        sheet2 = workbook.add_worksheet(_('Designs'))
        sheet2.write_row(0, 0, ['id', _('name'), _('default_code')])
        sheet2.set_column(0, 2, 20)
        for row, obj in enumerate(self.env['product.edesign'].search([]), 1):
            sheet2.write_row(row, 0, [obj.id, obj.name, obj.default_code or ''])

        sheet3 = workbook.add_worksheet(_("Design's Category"))
        sheet3.write_row(0, 0, ['id', _('display name'), _('default_code')])
        sheet3.set_column(0, 3, 20)
        for row, obj in enumerate(self.env['product.edesign.category'].search([]), 1):
            sheet3.write_row(row, 0, [obj.id,obj.display_name, obj.default_code or ''])
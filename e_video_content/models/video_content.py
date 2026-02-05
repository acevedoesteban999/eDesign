from odoo import models, fields, api


class VideoContent(models.Model):
    _name = 'video.content'
    _description = "Video Content"
    video_data = fields.Binary("Video File")
    filename = fields.Char("Filename")
    file_size = fields.Char("Size", compute="_compute_file_info", store=True)
    mimetype = fields.Char("Mime Type", compute="_compute_file_info", store=True)
    preview = fields.Image("Preview")
    
    @api.depends('video_data')
    def _compute_file_info(self):
        for record in self:
            attachment = self.env['ir.attachment'].sudo().search([
                ('res_model', '=', record._name),
                ('res_id', '=', record.id),
                ('res_field', '=', 'video_data')
            ], limit=1)
            if attachment:
                record.file_size = attachment.file_size
                record.mimetype = attachment.mimetype
            else:
                record.file_size = ""
                record.mimetype = ""
                record.filename = ""
                
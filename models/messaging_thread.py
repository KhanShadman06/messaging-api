# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MessagingThread(models.Model):
    _name = 'messaging.thread'
    _description = 'Messaging Thread for API'
    _order = 'create_date desc'

    name = fields.Char(string='Thread Name', required=True)
    partner_ids = fields.Many2many('res.partner', string='Participants')
    message_ids = fields.One2many('messaging.message', 'thread_id', string='Messages')
    thread_type = fields.Selection([
        ('sms', 'SMS'),
        ('chat', 'Chat'),
        ('group', 'Group')
    ], string='Thread Type', default='chat', required=True)
    active = fields.Boolean(default=True)
    last_message_date = fields.Datetime(string='Last Message Date', compute='_compute_last_message_date', store=True)

    @api.depends('message_ids.create_date')
    def _compute_last_message_date(self):
        for thread in self:
            if thread.message_ids:
                thread.last_message_date = max(thread.message_ids.mapped('create_date'))
            else:
                thread.last_message_date = False


class MessagingMessage(models.Model):
    _name = 'messaging.message'
    _description = 'Messaging Message for API'
    _order = 'create_date desc'

    thread_id = fields.Many2one('messaging.thread', string='Thread', required=True, ondelete='cascade')
    author_id = fields.Many2one('res.partner', string='Author', required=True)
    body = fields.Text(string='Message Body', required=True)
    message_type = fields.Selection([
        ('sms', 'SMS'),
        ('text', 'Text'),
    ], string='Message Type', default='text', required=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    phone_number = fields.Char(string='Phone Number')
    sms_status = fields.Selection([
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed')
    ], string='SMS Status', default='pending')
    is_read = fields.Boolean(string='Is Read', default=False)
    create_date = fields.Datetime(string='Created Date', readonly=True)

    def mark_as_read(self):
        self.write({'is_read': True})
        return True

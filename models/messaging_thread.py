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
    mail_channel_id = fields.Many2one('discuss.channel', string='Discuss Channel', copy=False, readonly=True)

    @api.depends('message_ids.create_date')
    def _compute_last_message_date(self):
        for thread in self:
            if thread.message_ids:
                thread.last_message_date = max(thread.message_ids.mapped('create_date'))
            else:
                thread.last_message_date = False

    def _channel_type_value(self):
        self.ensure_one()
        if self.thread_type == 'group':
            return 'group'
        return 'chat'

    def _ensure_mail_channel(self):
        channel_env = self.env['discuss.channel']
        if self.env.context.get('messaging_api_skip_channel_user'):
            channel_env = channel_env.with_context(install_mode=True)

        for thread in self:
            if thread.mail_channel_id:
                thread._sync_mail_channel()
                continue

            channel_vals = {
                'name': thread.name,
                'channel_type': thread._channel_type_value(),
                'channel_partner_ids': [(4, pid) for pid in thread.partner_ids.ids],
                'messaging_thread_id': thread.id,
            }
            channel = channel_env.create(channel_vals)
            thread.mail_channel_id = channel

    def _sync_mail_channel(self):
        for thread in self:
            if not thread.mail_channel_id:
                thread._ensure_mail_channel()
                continue

            channel = thread.mail_channel_id.sudo()
            updates = {}
            new_type = thread._channel_type_value()
            if channel.name != thread.name:
                updates['name'] = thread.name
            if channel.channel_type != new_type:
                updates['channel_type'] = new_type
            if 'active' in channel._fields:
                if channel.active != thread.active:
                    updates['active'] = thread.active
            if updates:
                channel.write(updates)

            if set(channel.channel_partner_ids.ids) != set(thread.partner_ids.ids):
                channel.write({'channel_partner_ids': [(6, 0, thread.partner_ids.ids)]})

            if channel.messaging_thread_id != thread:
                channel.write({'messaging_thread_id': thread.id})

    @api.model
    def create(self, vals):
        records = super().create(vals)
        records._ensure_mail_channel()
        return records

    def write(self, vals):
        res = super().write(vals)
        tracked_fields = {'name', 'thread_type', 'partner_ids', 'active'}
        if tracked_fields.intersection(vals.keys()):
            self._sync_mail_channel()
        return res

    def unlink(self):
        channels = self.mapped('mail_channel_id')
        res = super().unlink()
        if channels:
            channels.sudo().unlink()
        return res


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
    mail_message_id = fields.Many2one('mail.message', string='Discuss Message', copy=False, readonly=True)

    def mark_as_read(self):
        self.write({'is_read': True})
        return True

    @api.model
    def create(self, vals):
        records = super().create(vals)
        for record in records:
            if self.env.context.get('skip_mail_sync'):
                continue

            thread = record.thread_id
            thread._ensure_mail_channel()
            channel = thread.mail_channel_id
            if not channel:
                continue

            attachments = record.attachment_ids.ids if record.attachment_ids else []
            message_ctx = dict(self.env.context, skip_messaging_sync=True)
            mail_message = channel.with_context(message_ctx).message_post(
                body=record.body or '',
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
                author_id=record.author_id.id,
                attachment_ids=attachments,
            )
            if mail_message:
                record.mail_message_id = mail_message.id
        return records


class DiscussChannel(models.Model):
    _inherit = 'discuss.channel'

    messaging_thread_id = fields.Many2one('messaging.thread', string='Messaging Thread', copy=False)

    def message_post(self, **kwargs):
        mail_message = super().message_post(**kwargs)

        if self.env.context.get('skip_messaging_sync'):
            return mail_message

        message_records = mail_message
        if not isinstance(mail_message, models.Model):
            message_records = self.env['mail.message'].browse(mail_message)

        if not message_records:
            return mail_message

        if len(message_records) == len(self):
            channel_message_pairs = zip(self, message_records)
        else:
            last_message = message_records[len(message_records) - 1]
            channel_message_pairs = [(channel, last_message) for channel in self]

        MessagingMessage = self.env['messaging.message'].sudo()
        for channel, message_record in channel_message_pairs:
            if not channel.messaging_thread_id:
                continue

            author_partner = message_record.author_id or self.env.user.partner_id
            msg_vals = {
                'thread_id': channel.messaging_thread_id.id,
                'author_id': author_partner.id,
                'body': message_record.body or '',
                'message_type': 'text',
                'mail_message_id': message_record.id,
            }
            if message_record.attachment_ids:
                msg_vals['attachment_ids'] = [(6, 0, message_record.attachment_ids.ids)]

            MessagingMessage.with_context(skip_mail_sync=True).create(msg_vals)

        return mail_message

# -*- coding: utf-8 -*-

import json
import base64
from odoo import http
from odoo.http import request, Response
import logging

_logger = logging.getLogger(__name__)


class MessagingAPIController(http.Controller):

    def _serialize_partner(self, partner, include_contact=False):
        """Return payload info using linked user id when available."""
        user = partner.user_ids[:1]
        data = {
            'id': user.id if user else partner.id,
            'name': partner.name,
            'partner_id': partner.id,
            'user_id': user.id if user else None,
        }
        if include_contact:
            data.update({
                'email': partner.email,
                'phone': partner.phone,
                'mobile': partner.mobile,
            })
        return data

    def _normalize_partner_ids(self, identifiers):
        """Accept user or partner ids and always return partner ids."""
        if not identifiers:
            return []

        if not isinstance(identifiers, (list, tuple, set)):
            identifiers = [identifiers]

        env = request.env
        res_users = env['res.users'].sudo()
        res_partner = env['res.partner'].sudo()
        normalized = []
        seen = set()

        for identifier in identifiers:
            if identifier is None:
                continue
            try:
                identifier_int = int(identifier)
            except (TypeError, ValueError):
                continue

            partner_id = False
            user = res_users.browse(identifier_int)
            if user.exists() and user.partner_id:
                partner_id = user.partner_id.id
            else:
                partner = res_partner.browse(identifier_int)
                if partner.exists():
                    partner_id = partner.id

            if partner_id and partner_id not in seen:
                seen.add(partner_id)
                normalized.append(partner_id)

        return normalized

    # =====================
    # Message APIs (Text Chat)
    # =====================

    @http.route('/api/messaging/threads', type='json', auth='user', methods=['POST'], csrf=False)
    def get_threads(self, thread_type=None, **kwargs):
        """
        Get all messaging threads for the current user

        Parameters:
        - thread_type: Optional filter by type (sms, chat, group)

        Returns:
        - threads: List of threads
        """
        try:
            user_partner_id = request.env.user.partner_id.id
            domain = [('partner_ids', 'in', [user_partner_id])]

            if thread_type:
                domain.append(('thread_type', '=', thread_type))

            threads = request.env['messaging.thread'].search(domain)

            result = []
            for thread in threads:
                last_message = thread.message_ids[:1] if thread.message_ids else False
                unread_count = len(thread.message_ids.filtered(lambda m: not m.is_read and m.author_id.id != user_partner_id))

                result.append({
                    'id': thread.id,
                    'name': thread.name,
                    'type': thread.thread_type,
                    'participants': [self._serialize_partner(p) for p in thread.partner_ids],
                    'last_message': last_message.body if last_message else '',
                    'last_message_date': last_message.create_date.strftime('%Y-%m-%d %H:%M:%S') if last_message else '',
                    'unread_count': unread_count
                })

            return {'threads': result}

        except Exception as e:
            _logger.error(f"Error fetching threads: {str(e)}")
            return {'error': str(e)}

    @http.route('/api/messaging/thread/create', type='json', auth='user', methods=['POST'], csrf=False)
    def create_thread(self, name=None, partner_ids=None, thread_type='chat', **kwargs):
        """
        Create a new messaging thread

        Parameters:
        - name: Thread name
        - partner_ids: List of user or partner IDs to add as participants
        - thread_type: Type of thread (sms, chat, group)

        Returns:
        - thread_id: ID of created thread
        """
        try:
            if not name:
                return {'error': 'name is required'}

            user_partner_id = request.env.user.partner_id.id

            # Include current user in participants
            normalized_partner_ids = self._normalize_partner_ids(partner_ids) if partner_ids else []

            # Ensure current user is part of the conversation
            if user_partner_id not in normalized_partner_ids:
                normalized_partner_ids.append(user_partner_id)
            if not normalized_partner_ids:
                normalized_partner_ids = [user_partner_id]

            thread = request.env['messaging.thread'].create({
                'name': name,
                'thread_type': thread_type,
                'partner_ids': [(6, 0, normalized_partner_ids)]
            })

            return {
                'success': True,
                'thread_id': thread.id,
                'name': thread.name
            }

        except Exception as e:
            _logger.error(f"Error creating thread: {str(e)}")
            return {'error': str(e)}

    @http.route('/api/messaging/messages', type='json', auth='user', methods=['POST'], csrf=False)
    def get_messages(self, thread_id=None, limit=50, offset=0, **kwargs):
        """
        Get messages from a thread

        Parameters:
        - thread_id: ID of the thread
        - limit: Number of messages to fetch (default 50)
        - offset: Offset for pagination (default 0)

        Returns:
        - messages: List of messages
        """
        try:
            if not thread_id:
                return {'error': 'thread_id is required'}

            thread_id = int(thread_id)
            limit = int(limit) if limit else 50
            offset = int(offset) if offset else 0

            user_partner_id = request.env.user.partner_id.id
            _logger.info(
                "MessagingAPI: get_messages thread_id=%s limit=%s offset=%s user_partner=%s",
                thread_id,
                limit,
                offset,
                user_partner_id,
            )

            thread = request.env['messaging.thread'].browse(thread_id)
            if not thread.exists():
                return {'error': 'Thread not found'}

            # Check if user is participant
            if user_partner_id not in thread.partner_ids.ids:
                return {'error': 'Access denied'}

            messages = request.env['messaging.message'].search([
                ('thread_id', '=', thread_id)
            ], order='create_date desc', limit=limit, offset=offset)

            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            result = []
            for msg in messages:
                author_info = self._serialize_partner(msg.author_id)
                attachments = [{
                    'id': a.id,
                    'name': a.name,
                    'mimetype': a.mimetype,
                    'file_size': a.file_size,
                    'url': f"{base_url}/api/messaging/attachment/{a.id}",
                    'access_token': a.access_token
                } for a in msg.attachment_ids]

                result.append({
                    'id': msg.id,
                    'author_id': author_info['id'],
                    'author_partner_id': author_info['partner_id'],
                    'author_user_id': author_info['user_id'],
                    'author_name': author_info['name'],
                    'body': msg.body,
                    'message_type': msg.message_type,
                    'is_read': msg.is_read,
                    'created_date': msg.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'attachments': attachments
                })

            response = {
                'messages': result,
                'thread_id': thread_id,
                'thread_name': thread.name
            }
            _logger.info(
                "MessagingAPI: get_messages response_count=%s thread_id=%s",
                len(result),
                thread_id,
            )
            return response

        except Exception as e:
            _logger.error(f"Error fetching messages: {str(e)}")
            return {'error': str(e)}

    @http.route('/api/messaging/message/send', type='json', auth='user', methods=['POST'], csrf=False)
    def send_message(self, thread_id=None, body=None, attachment_ids=None, **kwargs):
        """
        Send a message to a thread

        Parameters:
        - thread_id: ID of the thread
        - body: Message body
        - attachment_ids: Optional list of attachment IDs

        Returns:
        - success: Boolean
        - message_id: ID of created message
        """
        try:
            if not thread_id or not body:
                return {'error': 'thread_id and body are required'}

            thread_id = int(thread_id)
            _logger.info(
                "MessagingAPI: send_message request thread_id=%s body=%s attachments=%s",
                thread_id,
                body,
                attachment_ids,
            )

            thread = request.env['messaging.thread'].browse(thread_id)

            if not thread.exists():
                return {'error': 'Thread not found'}

            # Check if user is participant
            user_partner_id = request.env.user.partner_id.id
            if user_partner_id not in thread.partner_ids.ids:
                return {'error': 'Access denied'}

            message_vals = {
                'thread_id': thread_id,
                'author_id': user_partner_id,
                'body': body,
                'message_type': 'text',
            }

            if attachment_ids:
                message_vals['attachment_ids'] = [(6, 0, attachment_ids)]

            message = request.env['messaging.message'].create(message_vals)

            response = {
                'success': True,
                'message_id': message.id,
                'created_date': message.create_date.strftime('%Y-%m-%d %H:%M:%S')
            }
            _logger.info(
                "MessagingAPI: send_message created message_id=%s thread_id=%s author_id=%s",
                message.id,
                thread_id,
                user_partner_id,
            )
            return response

        except Exception as e:
            _logger.error(f"Error sending message: {str(e)}")
            return {'error': str(e)}

    @http.route('/api/messaging/message/read', type='json', auth='user', methods=['POST'], csrf=False)
    def mark_message_read(self, message_id=None, message_ids=None, **kwargs):
        """
        Mark message(s) as read

        Parameters:
        - message_id: Single message ID
        - message_ids: List of message IDs

        Returns:
        - success: Boolean
        """
        try:
            if message_id:
                message_ids = [int(message_id)]
            elif message_ids:
                message_ids = [int(mid) for mid in message_ids]
            else:
                return {'error': 'message_id or message_ids required'}

            messages = request.env['messaging.message'].browse(message_ids)
            messages.mark_as_read()

            return {
                'success': True,
                'marked_count': len(messages)
            }

        except Exception as e:
            _logger.error(f"Error marking messages as read: {str(e)}")
            return {'error': str(e)}

    @http.route('/api/messaging/unread/count', type='json', auth='user', methods=['POST'], csrf=False)
    def get_unread_count(self, **kwargs):
        """
        Get total unread message count for current user

        Returns:
        - unread_count: Total unread messages
        - unread_by_thread: Unread count per thread
        """
        try:
            user_partner_id = request.env.user.partner_id.id

            threads = request.env['messaging.thread'].search([
                ('partner_ids', 'in', [user_partner_id])
            ])

            unread_by_thread = []
            total_unread = 0

            for thread in threads:
                unread_messages = thread.message_ids.filtered(
                    lambda m: not m.is_read and m.author_id.id != user_partner_id
                )
                count = len(unread_messages)

                if count > 0:
                    unread_by_thread.append({
                        'thread_id': thread.id,
                        'thread_name': thread.name,
                        'unread_count': count
                    })
                    total_unread += count

            return {
                'unread_count': total_unread,
                'unread_by_thread': unread_by_thread
            }

        except Exception as e:
            _logger.error(f"Error fetching unread count: {str(e)}")
            return {'error': str(e)}

    # =====================
    # Attachment APIs
    # =====================

    @http.route('/api/messaging/attachment/upload', type='http', auth='user', methods=['POST'], csrf=False)
    def upload_attachment(self, **kwargs):
        """
        Upload an attachment

        Parameters (multipart/form-data):
        - file: File to upload
        - name: Optional filename
        - thread_id: Optional thread ID to associate with

        Returns:
        - attachment_id: ID of created attachment
        """
        try:
            file_data = kwargs.get('file')
            if not file_data:
                return Response(
                    json.dumps({'error': 'No file provided'}),
                    content_type='application/json',
                    status=400
                )

            file_name = kwargs.get('name', file_data.filename)
            file_content = base64.b64encode(file_data.read())

            attachment_vals = {
                'name': file_name,
                'datas': file_content,
                'res_model': 'messaging.message',
                'res_id': 0,
            }

            attachment = request.env['ir.attachment'].sudo().create(attachment_vals)

            # If thread_id provided, can be used for context
            thread_id = kwargs.get('thread_id')

            return Response(
                json.dumps({
                    'success': True,
                    'attachment_id': attachment.id,
                    'name': attachment.name,
                    'mimetype': attachment.mimetype,
                    'file_size': attachment.file_size,
                    'access_token': attachment.access_token
                }),
                content_type='application/json',
                status=200
            )

        except Exception as e:
            _logger.error(f"Error uploading attachment: {str(e)}")
            return Response(
                json.dumps({'error': str(e)}),
                content_type='application/json',
                status=500
            )

    @http.route('/api/messaging/attachment/<int:attachment_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def download_attachment(self, attachment_id, access_token=None, **kwargs):
        """
        Download an attachment

        Parameters:
        - attachment_id: ID of the attachment
        - access_token: Optional access token

        Returns:
        - File content
        """
        try:
            attachment = request.env['ir.attachment'].sudo().browse(attachment_id)

            if not attachment.exists():
                return Response(
                    json.dumps({'error': 'Attachment not found'}),
                    content_type='application/json',
                    status=404
                )

            # Verify access token if provided
            if access_token and attachment.access_token != access_token:
                return Response(
                    json.dumps({'error': 'Invalid access token'}),
                    content_type='application/json',
                    status=403
                )

            if not attachment.datas:
                return Response(
                    json.dumps({'error': 'No file data'}),
                    content_type='application/json',
                    status=404
                )

            file_content = base64.b64decode(attachment.datas)

            headers = [
                ('Content-Type', attachment.mimetype or 'application/octet-stream'),
                ('Content-Disposition', f'attachment; filename="{attachment.name}"'),
                ('Content-Length', len(file_content))
            ]

            return request.make_response(file_content, headers=headers)

        except Exception as e:
            _logger.error(f"Error downloading attachment: {str(e)}")
            return Response(
                json.dumps({'error': str(e)}),
                content_type='application/json',
                status=500
            )

    @http.route('/api/messaging/attachment/delete/<int:attachment_id>', type='json', auth='user', methods=['POST'], csrf=False)
    def delete_attachment(self, attachment_id, **kwargs):
        """
        Delete an attachment

        Parameters:
        - attachment_id: ID of the attachment

        Returns:
        - success: Boolean
        """
        try:
            attachment = request.env['ir.attachment'].sudo().browse(attachment_id)

            if not attachment.exists():
                return {'error': 'Attachment not found'}

            # Check if user is the owner or has access
            user_partner_id = request.env.user.partner_id.id

            # Find if attachment is linked to any message
            messages = request.env['messaging.message'].search([
                ('attachment_ids', 'in', [attachment_id])
            ])

            # Check if user is author of any message with this attachment
            if not any(msg.author_id.id == user_partner_id for msg in messages):
                return {'error': 'Access denied'}

            attachment.unlink()

            return {
                'success': True,
                'attachment_id': attachment_id
            }

        except Exception as e:
            _logger.error(f"Error deleting attachment: {str(e)}")
            return {'error': str(e)}

    @http.route('/api/messaging/attachment/info/<int:attachment_id>', type='json', auth='user', methods=['POST'], csrf=False)
    def get_attachment_info(self, attachment_id, **kwargs):
        """
        Get attachment information

        Parameters:
        - attachment_id: ID of the attachment

        Returns:
        - Attachment details
        """
        try:
            attachment = request.env['ir.attachment'].sudo().browse(attachment_id)

            if not attachment.exists():
                return {'error': 'Attachment not found'}

            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            return {
                'id': attachment.id,
                'name': attachment.name,
                'mimetype': attachment.mimetype,
                'file_size': attachment.file_size,
                'url': f"{base_url}/api/messaging/attachment/{attachment.id}",
                'access_token': attachment.access_token,
                'create_date': attachment.create_date.strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            _logger.error(f"Error fetching attachment info: {str(e)}")
            return {'error': str(e)}

    # =====================
    # Search & Discovery
    # =====================

    @http.route('/api/messaging/partners/search', type='json', auth='user', methods=['POST'], csrf=False)
    def search_partners(self, query=None, limit=20, **kwargs):
        """
        Search for partners to start a conversation

        Parameters:
        - query: Search query string
        - limit: Maximum results (default 20)

        Returns:
        - partners: List of matching partners
        """
        try:
            if not query:
                return {'error': 'query parameter is required'}

            limit = int(limit) if limit else 20

            partners = request.env['res.partner'].sudo().search([
                '|', '|',
                ('name', 'ilike', query),
                ('email', 'ilike', query),
                ('phone', 'ilike', query)
            ], limit=limit)

            result = []
            for partner in partners:
                result.append(self._serialize_partner(partner, include_contact=True))

            return {'partners': result}

        except Exception as e:
            _logger.error(f"Error searching partners: {str(e)}")
            return {'error': str(e)}

    @http.route('/api/messaging/thread/participants/<int:thread_id>', type='json', auth='user', methods=['POST'], csrf=False)
    def get_thread_participants(self, thread_id, **kwargs):
        """
        Get participants of a thread

        Parameters:
        - thread_id: ID of the thread

        Returns:
        - participants: List of participants
        """
        try:
            thread = request.env['messaging.thread'].browse(thread_id)

            if not thread.exists():
                return {'error': 'Thread not found'}

            # Check if user is participant
            user_partner_id = request.env.user.partner_id.id
            if user_partner_id not in thread.partner_ids.ids:
                return {'error': 'Access denied'}

            result = []
            for partner in thread.partner_ids:
                result.append(self._serialize_partner(partner, include_contact=True))

            return {
                'thread_id': thread_id,
                'thread_name': thread.name,
                'participants': result
            }

        except Exception as e:
            _logger.error(f"Error fetching thread participants: {str(e)}")
            return {'error': str(e)}

    @http.route('/api/messaging/thread/add_participant', type='json', auth='user', methods=['POST'], csrf=False)
    def add_thread_participant(self, thread_id=None, partner_id=None, **kwargs):
        """
        Add a participant to a thread

        Parameters:
        - thread_id: ID of the thread
        - partner_id: ID of user or partner to add

        Returns:
        - success: Boolean
        """
        try:
            if not thread_id or not partner_id:
                return {'error': 'thread_id and partner_id are required'}

            thread = request.env['messaging.thread'].browse(int(thread_id))

            if not thread.exists():
                return {'error': 'Thread not found'}

            # Check if user is participant
            user_partner_id = request.env.user.partner_id.id
            if user_partner_id not in thread.partner_ids.ids:
                return {'error': 'Access denied'}

            normalized_ids = self._normalize_partner_ids([partner_id])
            if not normalized_ids:
                return {'error': 'Participant not found'}

            participant_partner_id = normalized_ids[0]
            if participant_partner_id not in thread.partner_ids.ids:
                thread.write({
                    'partner_ids': [(4, participant_partner_id)]
                })

            partner_record = request.env['res.partner'].sudo().browse(participant_partner_id)
            participant_info = self._serialize_partner(partner_record)

            return {
                'success': True,
                'thread_id': thread.id,
                'partner_id': participant_info['partner_id'],
                'user_id': participant_info['user_id'],
                'participant': participant_info
            }

        except Exception as e:
            _logger.error(f"Error adding participant: {str(e)}")
            return {'error': str(e)}

    # =====================
    # Real-Time / Long Polling APIs
    # =====================

    @http.route('/api/messaging/poll/messages', type='json', auth='user', methods=['POST'], csrf=False)
    def poll_messages(self, thread_id=None, last_message_id=None, timeout=30, **kwargs):
        """
        Long polling endpoint for real-time messages
        Waits up to timeout seconds for new messages

        Parameters:
        - thread_id: ID of the thread to monitor
        - last_message_id: ID of the last message client has (optional)
        - timeout: Maximum seconds to wait (default 30, max 60)

        Returns:
        - messages: List of new messages
        - has_new: Boolean indicating if there are new messages
        """
        try:
            if not thread_id:
                return {'error': 'thread_id is required'}

            thread_id = int(thread_id)
            timeout = min(int(timeout) if timeout else 30, 60)  # Max 60 seconds
            last_message_id = int(last_message_id) if last_message_id else 0

            user_partner_id = request.env.user.partner_id.id
            _logger.info(
                "MessagingAPI: poll_messages start thread_id=%s last_message_id=%s timeout=%s user_partner=%s",
                thread_id,
                last_message_id,
                timeout,
                user_partner_id,
            )

            thread = request.env['messaging.thread'].browse(thread_id)
            if not thread.exists():
                return {'error': 'Thread not found'}

            # Check if user is participant
            if user_partner_id not in thread.partner_ids.ids:
                return {'error': 'Access denied'}

            import time
            start_time = time.time()
            poll_interval = 1  # Check every 1 second

            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            while (time.time() - start_time) < timeout:
                # Search for new messages
                domain = [
                    ('thread_id', '=', thread_id),
                ]
                if last_message_id:
                    domain.append(('id', '>', last_message_id))

                new_messages = request.env['messaging.message'].search(
                    domain,
                    order='create_date asc'
                )

                if new_messages:
                    result = []
                    for msg in new_messages:
                        author_info = self._serialize_partner(msg.author_id)
                        attachments = [{
                            'id': a.id,
                            'name': a.name,
                            'mimetype': a.mimetype,
                            'file_size': a.file_size,
                            'url': f"{base_url}/api/messaging/attachment/{a.id}",
                            'access_token': a.access_token
                        } for a in msg.attachment_ids]

                        result.append({
                            'id': msg.id,
                            'author_id': author_info['id'],
                            'author_partner_id': author_info['partner_id'],
                            'author_user_id': author_info['user_id'],
                            'author_name': author_info['name'],
                            'body': msg.body,
                            'message_type': msg.message_type,
                            'is_read': msg.is_read,
                            'created_date': msg.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'attachments': attachments
                        })

                    response = {
                        'has_new': True,
                        'messages': result,
                        'count': len(result)
                    }
                    _logger.info(
                        "MessagingAPI: poll_messages new_messages=%s thread_id=%s last_message_id=%s",
                        len(result),
                        thread_id,
                        last_message_id,
                    )
                    return response

                # Wait before checking again
                time.sleep(poll_interval)

            # Timeout reached, no new messages
            response = {
                'has_new': False,
                'messages': [],
                'count': 0
            }
            _logger.info(
                "MessagingAPI: poll_messages timeout thread_id=%s last_message_id=%s",
                thread_id,
                last_message_id,
            )
            return response

        except Exception as e:
            _logger.error(f"Error in long polling: {str(e)}")
            return {'error': str(e)}

    @http.route('/api/messaging/poll/updates', type='json', auth='user', methods=['POST'], csrf=False)
    def poll_all_updates(self, last_check=None, timeout=30, **kwargs):
        """
        Long polling for all updates across all threads
        Returns unread counts, new messages, typing indicators

        Parameters:
        - last_check: Last check timestamp (ISO format)
        - timeout: Maximum seconds to wait (default 30, max 60)

        Returns:
        - has_updates: Boolean
        - unread_count: Total unread count
        - threads_with_updates: List of threads that have updates
        """
        try:
            timeout = min(int(timeout) if timeout else 30, 60)
            user_partner_id = request.env.user.partner_id.id

            import time
            from datetime import datetime
            start_time = time.time()
            poll_interval = 2

            # Get initial unread count
            threads = request.env['messaging.thread'].search([
                ('partner_ids', 'in', [user_partner_id])
            ])

            initial_unread = sum([
                len(t.message_ids.filtered(lambda m: not m.is_read and m.author_id.id != user_partner_id))
                for t in threads
            ])

            while (time.time() - start_time) < timeout:
                # Check for new unread messages
                current_unread = sum([
                    len(t.message_ids.filtered(lambda m: not m.is_read and m.author_id.id != user_partner_id))
                    for t in threads
                ])

                if current_unread != initial_unread:
                    # Something changed, return updates
                    threads_with_updates = []
                    for thread in threads:
                        unread_messages = thread.message_ids.filtered(
                            lambda m: not m.is_read and m.author_id.id != user_partner_id
                        )
                        if unread_messages:
                            threads_with_updates.append({
                                'thread_id': thread.id,
                                'thread_name': thread.name,
                                'unread_count': len(unread_messages),
                                'last_message': unread_messages[0].body if unread_messages else '',
                                'last_message_date': unread_messages[0].create_date.strftime('%Y-%m-%d %H:%M:%S') if unread_messages else ''
                            })

                    return {
                        'has_updates': True,
                        'unread_count': current_unread,
                        'threads_with_updates': threads_with_updates
                    }

                time.sleep(poll_interval)

            # Timeout, no updates
            return {
                'has_updates': False,
                'unread_count': initial_unread,
                'threads_with_updates': []
            }

        except Exception as e:
            _logger.error(f"Error in poll updates: {str(e)}")
            return {'error': str(e)}

    # =====================
    # Typing Indicators
    # =====================

    @http.route('/api/messaging/typing/start', type='json', auth='user', methods=['POST'], csrf=False)
    def typing_start(self, thread_id=None, **kwargs):
        """
        Indicate that user is typing in a thread

        Parameters:
        - thread_id: ID of the thread

        Returns:
        - success: Boolean
        """
        try:
            if not thread_id:
                return {'error': 'thread_id is required'}

            thread_id = int(thread_id)
            user = request.env.user
            partner = user.partner_id

            # Store typing status in cache (using ir.config_parameter as simple storage)
            cache_key = f'typing_{thread_id}_{partner.id}'

            from datetime import datetime, timedelta
            import json

            typing_data = {
                'partner_id': partner.id,
                'partner_name': partner.name,
                'thread_id': thread_id,
                'timestamp': datetime.now().isoformat()
            }

            # In production, use Redis or memcached. For now, use simple approach
            # This is a simplified version - ideally use bus.bus or similar

            return {
                'success': True,
                'partner_id': partner.id,
                'user_id': user.id
            }

        except Exception as e:
            _logger.error(f"Error in typing start: {str(e)}")
            return {'error': str(e)}

    @http.route('/api/messaging/typing/stop', type='json', auth='user', methods=['POST'], csrf=False)
    def typing_stop(self, thread_id=None, **kwargs):
        """
        Indicate that user stopped typing

        Parameters:
        - thread_id: ID of the thread

        Returns:
        - success: Boolean
        """
        try:
            if not thread_id:
                return {'error': 'thread_id is required'}

            thread_id = int(thread_id)
            user = request.env.user
            partner = user.partner_id

            return {
                'success': True,
                'partner_id': partner.id,
                'user_id': user.id
            }

        except Exception as e:
            _logger.error(f"Error in typing stop: {str(e)}")
            return {'error': str(e)}

    @http.route('/api/messaging/typing/status/<int:thread_id>', type='json', auth='user', methods=['POST'], csrf=False)
    def typing_status(self, thread_id, **kwargs):
        """
        Get who is currently typing in a thread

        Parameters:
        - thread_id: ID of the thread

        Returns:
        - typing_users: List of users currently typing
        """
        try:
            # This is a placeholder - in production, implement with Redis/cache
            # For now, return empty as we don't have persistent cache

            return {
                'thread_id': thread_id,
                'typing_users': []
            }

        except Exception as e:
            _logger.error(f"Error getting typing status: {str(e)}")
            return {'error': str(e)}

    # =====================
    # Presence / Online Status
    # =====================

    @http.route('/api/messaging/presence/update', type='json', auth='user', methods=['POST'], csrf=False)
    def update_presence(self, status='online', **kwargs):
        """
        Update user's online presence status

        Parameters:
        - status: online, away, offline

        Returns:
        - success: Boolean
        """
        try:
            user = request.env.user
            partner = user.partner_id

            # Update last seen time
            partner.sudo().write({
                'write_date': request.env.cr.now()
            })

            return {
                'success': True,
                'partner_id': partner.id,
                'user_id': user.id,
                'status': status
            }

        except Exception as e:
            _logger.error(f"Error updating presence: {str(e)}")
            return {'error': str(e)}

    @http.route('/api/messaging/presence/status', type='json', auth='user', methods=['POST'], csrf=False)
    def get_presence_status(self, partner_ids=None, **kwargs):
        """
        Get online status of specific partners

        Parameters:
        - partner_ids: List of user or partner IDs to check

        Returns:
        - presence: List of partner presence info
        """
        try:
            if not partner_ids:
                return {'error': 'partner_ids required'}

            normalized_ids = self._normalize_partner_ids(partner_ids)
            if not normalized_ids:
                return {'error': 'No valid partners found'}

            from datetime import datetime, timedelta

            partners = request.env['res.partner'].sudo().browse(normalized_ids)

            result = []
            for partner in partners:
                # Consider online if last activity within 5 minutes
                is_online = False
                last_seen = None

                if partner.write_date:
                    time_diff = datetime.now() - partner.write_date
                    is_online = time_diff < timedelta(minutes=5)
                    last_seen = partner.write_date.strftime('%Y-%m-%d %H:%M:%S')

                partner_info = self._serialize_partner(partner)
                partner_info.update({
                    'status': 'online' if is_online else 'offline',
                    'last_seen': last_seen
                })

                result.append(partner_info)

            return {
                'presence': result
            }

        except Exception as e:
            _logger.error(f"Error getting presence: {str(e)}")
            return {'error': str(e)}

    # =====================
    # Notifications
    # =====================

    @http.route('/api/messaging/notifications/count', type='json', auth='user', methods=['POST'], csrf=False)
    def get_notification_count(self, **kwargs):
        """
        Get total notification count (unread messages)

        Returns:
        - total_count: Total unread messages across all threads
        - by_type: Breakdown by thread type
        """
        try:
            user_partner_id = request.env.user.partner_id.id

            threads = request.env['messaging.thread'].search([
                ('partner_ids', 'in', [user_partner_id])
            ])

            total = 0
            by_type = {
                'chat': 0,
                'group': 0,
                'sms': 0
            }

            for thread in threads:
                unread = thread.message_ids.filtered(
                    lambda m: not m.is_read and m.author_id.id != user_partner_id
                )
                count = len(unread)
                total += count
                if thread.thread_type in by_type:
                    by_type[thread.thread_type] += count

            return {
                'total_count': total,
                'by_type': by_type
            }

        except Exception as e:
            _logger.error(f"Error getting notification count: {str(e)}")
            return {'error': str(e)}

    @http.route('/api/messaging/notifications/mark_all_read', type='json', auth='user', methods=['POST'], csrf=False)
    def mark_all_notifications_read(self, thread_id=None, **kwargs):
        """
        Mark all messages in a thread as read

        Parameters:
        - thread_id: Optional thread ID (if not provided, marks all messages as read)

        Returns:
        - success: Boolean
        - marked_count: Number of messages marked as read
        """
        try:
            user_partner_id = request.env.user.partner_id.id

            domain = [
                ('is_read', '=', False),
                ('author_id', '!=', user_partner_id)
            ]

            if thread_id:
                domain.append(('thread_id', '=', int(thread_id)))
            else:
                # Only mark messages in threads where user is participant
                threads = request.env['messaging.thread'].search([
                    ('partner_ids', 'in', [user_partner_id])
                ])
                domain.append(('thread_id', 'in', threads.ids))

            messages = request.env['messaging.message'].search(domain)
            count = len(messages)
            messages.write({'is_read': True})

            return {
                'success': True,
                'marked_count': count
            }

        except Exception as e:
            _logger.error(f"Error marking all as read: {str(e)}")
            return {'error': str(e)}

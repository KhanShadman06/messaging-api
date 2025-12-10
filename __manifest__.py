# -*- coding: utf-8 -*-
{
    'name': "Messaging API",
    'summary': """
        REST API for messaging operations including SMS, attachments, and message history
    """,
    'description': """
        Provides REST API endpoints for:
        - Sending and receiving SMS messages
        - Managing message attachments
        - Retrieving message history
        - Integration with third-party mobile applications
    """,
    'author': "Your Company",
    'website': "https://www.yourcompany.com",
    'category': 'Discuss',
    'version': '17.0.1.0.0',
    'depends': [
        'base',
        'mail',
        'sms',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}

def post_init_hook(env):
    env['messaging.thread'].sudo().with_context(messaging_api_skip_channel_user=True).search([
        ('mail_channel_id', '=', False),
    ])._ensure_mail_channel()

# Messaging API - Installation Guide

## Quick Installation Steps

### 1. Copy Module to Addons Directory

The module is already in your custom addons directory:
```
/home/shadman/docker/custom_addons/messaging_api/
```

### 2. Restart Odoo Server

Restart your Odoo server to load the new module:
```bash
# If using docker
docker restart <your_odoo_container_name>

# Or if running Odoo directly
sudo systemctl restart odoo
```

### 3. Update Apps List

1. Log in to Odoo as Administrator
2. Go to **Apps** menu
3. Click **Update Apps List** button
4. Confirm the update

### 4. Install the Module

1. In the Apps menu, remove the "Apps" filter to show all modules
2. Search for "Messaging API"
3. Click **Install** button

### 5. Configure SMS Provider (Optional)

If you want to use SMS features, configure an SMS provider:

1. Go to **Settings** → **Technical** → **SMS**
2. Configure your SMS gateway (Twilio, etc.)
3. Set up the IAP account for SMS

### 6. Verify Installation

Check if the module is installed correctly:

1. Go to **Settings** → **Technical** → **Database Structure** → **Models**
2. Search for `messaging.thread` and `messaging.message`
3. Both models should appear

### 7. Test the API

Use the provided examples in README.md to test the API endpoints.

**Example Test (using curl):**

```bash
# Login first to get session
curl -X POST \
  http://localhost:8069/web/session/authenticate \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "params": {
      "db": "your_database",
      "login": "admin",
      "password": "admin"
    }
  }'

# Then test getting threads
curl -X POST \
  http://localhost:8069/api/messaging/threads \
  -H 'Content-Type: application/json' \
  -H 'Cookie: session_id=YOUR_SESSION_ID' \
  -d '{
    "jsonrpc": "2.0",
    "params": {}
  }'
```

## Troubleshooting

### Module Not Appearing in Apps List

- Ensure Odoo server was restarted after copying the module
- Check file permissions (Odoo needs read access)
- Verify the module path is in `addons_path` configuration

### Permission Errors

- Check security/ir.model.access.csv is loaded
- Ensure user has proper access rights

### SMS Not Working

- Verify SMS provider is configured
- Check IAP credits
- Review Odoo logs for SMS errors

### API Returns 404

- Verify module is installed and activated
- Check Odoo is running on the expected port
- Ensure URL path is correct

## Module Structure

```
messaging_api/
├── __init__.py                         # Module initialization
├── __manifest__.py                     # Module metadata
├── README.md                           # API documentation
├── INSTALL.md                          # This file
├── controllers/
│   ├── __init__.py
│   └── messaging_api_controller.py     # All API endpoints
├── models/
│   ├── __init__.py
│   └── messaging_thread.py             # Data models
└── security/
    └── ir.model.access.csv             # Access control
```

## Dependencies

This module requires:
- **base**: Core Odoo functionality
- **mail**: Mail/messaging infrastructure
- **sms**: SMS sending capabilities

All dependencies are standard Odoo modules.

## Uninstallation

To uninstall the module:

1. Go to **Apps**
2. Search for "Messaging API"
3. Click the three dots ⋮ on the module
4. Select **Uninstall**
5. Confirm uninstallation

**Note:** Uninstalling will delete all messaging threads and messages created through this module.

## Upgrade

To upgrade the module after making changes:

1. Update the version in `__manifest__.py`
2. Restart Odoo server
3. Go to **Apps** → find "Messaging API"
4. Click **Upgrade**

## Development Mode

For development and testing:

```bash
# Start Odoo with development mode
./odoo-bin -c odoo.conf -d your_database --dev=all
```

This enables:
- Auto-reload on file changes
- Detailed error messages
- Asset debugging

## Support & Documentation

- Full API documentation: See README.md
- Code examples: See README.md integration section
- Model reference: See models/messaging_thread.py

## Next Steps

After installation:

1. Review the API documentation in README.md
2. Test endpoints using the provided examples
3. Configure SMS provider if using SMS features
4. Integrate with your mobile app or third-party service
5. Set up webhooks for SMS receiving (if needed)

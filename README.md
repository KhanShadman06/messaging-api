# Messaging API Module

A comprehensive REST API module for Odoo 17 that provides messaging capabilities including SMS, text messaging, and file attachments. This module is designed to integrate seamlessly with third-party mobile applications.

## Features

- **SMS Messaging**: Send and receive SMS messages
- **Text Messaging**: Create threads and send text messages
- **File Attachments**: Upload, download, and manage file attachments
- **Thread Management**: Create and manage conversation threads
- **Real-time Messaging**: Support for group chats and direct messages
- **Unread Message Tracking**: Track read/unread status
- **Partner Search**: Find users to start conversations

## Installation

1. Copy the `messaging_api` folder to your Odoo addons directory
2. Update the addons list: Go to Apps → Update Apps List
3. Search for "Messaging API" and install the module

## Dependencies

- base
- mail
- sms

## API Endpoints

All endpoints use JSON format and require authentication (`auth='user'`).

### Authentication

Use Odoo's standard authentication mechanism. Include the session ID in cookies or use API keys.

Example authentication headers:
```
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

---

## SMS APIs

### 1. Send SMS

**Endpoint:** `/api/messaging/sms/send`

**Method:** POST

**Parameters:**
```json
{
  "phone_number": "+1234567890",
  "message": "Hello from Odoo!"
}
```

**Response:**
```json
{
  "success": true,
  "message_id": 123,
  "sms_id": 456,
  "status": "sent"
}
```

---

### 2. Receive SMS (Webhook)

**Endpoint:** `/api/messaging/sms/receive`

**Method:** POST

**Parameters:**
```json
{
  "phone_number": "+1234567890",
  "message": "Incoming SMS message"
}
```

**Response:**
```json
{
  "success": true,
  "message_id": 124
}
```

---

### 3. Get SMS Threads

**Endpoint:** `/api/messaging/sms/threads`

**Method:** POST

**Response:**
```json
{
  "threads": [
    {
      "id": 1,
      "name": "+1234567890",
      "phone_number": "+1234567890",
      "last_message": "Hello!",
      "last_message_date": "2025-12-03 10:30:00",
      "unread_count": 2
    }
  ]
}
```

---

### 4. Get SMS Status

**Endpoint:** `/api/messaging/sms/status/<message_id>`

**Method:** POST

**Response:**
```json
{
  "message_id": 123,
  "status": "delivered",
  "phone_number": "+1234567890",
  "sent_date": "2025-12-03 10:30:00"
}
```

---

## Messaging APIs

### 5. Get All Threads

**Endpoint:** `/api/messaging/threads`

**Method:** POST

**Parameters (Optional):**
```json
{
  "thread_type": "chat"
}
```

**Response:**
```json
{
  "threads": [
    {
      "id": 1,
      "name": "Support Team",
      "type": "group",
      "participants": [
        {"id": 1, "name": "John Doe"},
        {"id": 2, "name": "Jane Smith"}
      ],
      "last_message": "How can I help?",
      "last_message_date": "2025-12-03 10:30:00",
      "unread_count": 5
    }
  ]
}
```

---

### 6. Create Thread

**Endpoint:** `/api/messaging/thread/create`

**Method:** POST

**Parameters:**
```json
{
  "name": "Project Discussion",
  "partner_ids": [1, 2, 3],
  "thread_type": "group"
}
```

**Response:**
```json
{
  "success": true,
  "thread_id": 10,
  "name": "Project Discussion"
}
```

---

### 7. Get Messages

**Endpoint:** `/api/messaging/messages`

**Method:** POST

**Parameters:**
```json
{
  "thread_id": 1,
  "limit": 50,
  "offset": 0
}
```

**Response:**
```json
{
  "messages": [
    {
      "id": 100,
      "author_id": 1,
      "author_name": "John Doe",
      "body": "Hello everyone!",
      "message_type": "text",
      "is_read": true,
      "created_date": "2025-12-03 10:30:00",
      "attachments": [
        {
          "id": 1,
          "name": "document.pdf",
          "mimetype": "application/pdf",
          "file_size": 1024000,
          "url": "http://your-domain.com/api/messaging/attachment/1",
          "access_token": "abc123xyz"
        }
      ]
    }
  ],
  "thread_id": 1,
  "thread_name": "Support Team"
}
```

---

### 8. Send Message

**Endpoint:** `/api/messaging/message/send`

**Method:** POST

**Parameters:**
```json
{
  "thread_id": 1,
  "body": "This is my message",
  "attachment_ids": [1, 2]
}
```

**Response:**
```json
{
  "success": true,
  "message_id": 101,
  "created_date": "2025-12-03 10:35:00"
}
```

---

### 9. Mark Message as Read

**Endpoint:** `/api/messaging/message/read`

**Method:** POST

**Parameters:**
```json
{
  "message_id": 100
}
```

Or mark multiple:
```json
{
  "message_ids": [100, 101, 102]
}
```

**Response:**
```json
{
  "success": true,
  "marked_count": 3
}
```

---

### 10. Get Unread Count

**Endpoint:** `/api/messaging/unread/count`

**Method:** POST

**Response:**
```json
{
  "unread_count": 15,
  "unread_by_thread": [
    {
      "thread_id": 1,
      "thread_name": "Support Team",
      "unread_count": 10
    },
    {
      "thread_id": 2,
      "thread_name": "Sales Discussion",
      "unread_count": 5
    }
  ]
}
```

---

## Attachment APIs

### 11. Upload Attachment

**Endpoint:** `/api/messaging/attachment/upload`

**Method:** POST (multipart/form-data)

**Parameters:**
- `file`: File to upload (multipart)
- `name`: Optional filename
- `thread_id`: Optional thread ID

**Example (cURL):**
```bash
curl -X POST \
  http://your-domain.com/api/messaging/attachment/upload \
  -H 'Cookie: session_id=YOUR_SESSION_ID' \
  -F 'file=@/path/to/file.pdf' \
  -F 'name=document.pdf'
```

**Response:**
```json
{
  "success": true,
  "attachment_id": 1,
  "name": "document.pdf",
  "mimetype": "application/pdf",
  "file_size": 1024000,
  "access_token": "abc123xyz"
}
```

---

### 12. Download Attachment

**Endpoint:** `/api/messaging/attachment/<attachment_id>`

**Method:** GET

**Parameters:**
- `access_token`: Optional access token (query parameter)

**Example:**
```
http://your-domain.com/api/messaging/attachment/1?access_token=abc123xyz
```

**Response:** Binary file download

---

### 13. Delete Attachment

**Endpoint:** `/api/messaging/attachment/delete/<attachment_id>`

**Method:** POST

**Response:**
```json
{
  "success": true,
  "attachment_id": 1
}
```

---

### 14. Get Attachment Info

**Endpoint:** `/api/messaging/attachment/info/<attachment_id>`

**Method:** POST

**Response:**
```json
{
  "id": 1,
  "name": "document.pdf",
  "mimetype": "application/pdf",
  "file_size": 1024000,
  "url": "http://your-domain.com/api/messaging/attachment/1",
  "access_token": "abc123xyz",
  "create_date": "2025-12-03 10:30:00"
}
```

---

## Search & Discovery APIs

### 15. Search Partners

**Endpoint:** `/api/messaging/partners/search`

**Method:** POST

**Parameters:**
```json
{
  "query": "john",
  "limit": 20
}
```

**Response:**
```json
{
  "partners": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1234567890",
      "mobile": "+0987654321"
    }
  ]
}
```

---

### 16. Get Thread Participants

**Endpoint:** `/api/messaging/thread/participants/<thread_id>`

**Method:** POST

**Response:**
```json
{
  "thread_id": 1,
  "thread_name": "Support Team",
  "participants": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1234567890"
    }
  ]
}
```

---

### 17. Add Thread Participant

**Endpoint:** `/api/messaging/thread/add_participant`

**Method:** POST

**Parameters:**
```json
{
  "thread_id": 1,
  "partner_id": 5
}
```

**Response:**
```json
{
  "success": true,
  "thread_id": 1,
  "partner_id": 5
}
```

---

## Integration Examples

### Python Example

```python
import requests
import json

# Configuration
BASE_URL = "http://your-odoo-domain.com"
SESSION_ID = "your_session_id"

headers = {
    'Content-Type': 'application/json',
    'Cookie': f'session_id={SESSION_ID}'
}

# Send SMS
def send_sms(phone, message):
    url = f"{BASE_URL}/api/messaging/sms/send"
    payload = {
        "jsonrpc": "2.0",
        "params": {
            "phone_number": phone,
            "message": message
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Get threads
def get_threads():
    url = f"{BASE_URL}/api/messaging/threads"
    payload = {
        "jsonrpc": "2.0",
        "params": {}
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Send message
def send_message(thread_id, body):
    url = f"{BASE_URL}/api/messaging/message/send"
    payload = {
        "jsonrpc": "2.0",
        "params": {
            "thread_id": thread_id,
            "body": body
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Upload attachment
def upload_file(file_path):
    url = f"{BASE_URL}/api/messaging/attachment/upload"
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url, files=files, headers={'Cookie': f'session_id={SESSION_ID}'})
    return response.json()
```

---

### JavaScript/React Example

```javascript
const API_BASE = 'http://your-odoo-domain.com';
const SESSION_ID = 'your_session_id';

// Send Message
async function sendMessage(threadId, body) {
  const response = await fetch(`${API_BASE}/api/messaging/message/send`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Cookie': `session_id=${SESSION_ID}`
    },
    credentials: 'include',
    body: JSON.stringify({
      jsonrpc: '2.0',
      params: {
        thread_id: threadId,
        body: body
      }
    })
  });
  return await response.json();
}

// Get Messages
async function getMessages(threadId, limit = 50) {
  const response = await fetch(`${API_BASE}/api/messaging/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Cookie': `session_id=${SESSION_ID}`
    },
    credentials: 'include',
    body: JSON.stringify({
      jsonrpc: '2.0',
      params: {
        thread_id: threadId,
        limit: limit
      }
    })
  });
  return await response.json();
}

// Upload Attachment
async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/api/messaging/attachment/upload`, {
    method: 'POST',
    headers: {
      'Cookie': `session_id=${SESSION_ID}`
    },
    credentials: 'include',
    body: formData
  });
  return await response.json();
}
```

---

### Mobile App (React Native) Example

```javascript
import axios from 'axios';

const API_BASE = 'http://your-odoo-domain.com';

// Configure axios
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true
});

// Send SMS
export const sendSMS = async (phoneNumber, message) => {
  try {
    const response = await api.post('/api/messaging/sms/send', {
      jsonrpc: '2.0',
      params: {
        phone_number: phoneNumber,
        message: message
      }
    });
    return response.data.result;
  } catch (error) {
    console.error('Error sending SMS:', error);
    throw error;
  }
};

// Get Threads
export const getThreads = async (threadType = null) => {
  try {
    const response = await api.post('/api/messaging/threads', {
      jsonrpc: '2.0',
      params: threadType ? { thread_type: threadType } : {}
    });
    return response.data.result.threads;
  } catch (error) {
    console.error('Error fetching threads:', error);
    throw error;
  }
};

// Send Message with Attachment
export const sendMessageWithAttachment = async (threadId, body, fileUri) => {
  try {
    let attachmentId = null;

    // Upload file first if provided
    if (fileUri) {
      const formData = new FormData();
      formData.append('file', {
        uri: fileUri,
        type: 'image/jpeg',
        name: 'photo.jpg'
      });

      const uploadResponse = await api.post('/api/messaging/attachment/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      });
      attachmentId = uploadResponse.data.attachment_id;
    }

    // Send message
    const response = await api.post('/api/messaging/message/send', {
      jsonrpc: '2.0',
      params: {
        thread_id: threadId,
        body: body,
        attachment_ids: attachmentId ? [attachmentId] : []
      }
    });
    return response.data.result;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};
```

---

## Error Handling

All API endpoints return errors in the following format:

```json
{
  "error": "Error message description"
}
```

Common error messages:
- `"Missing required parameter: <param_name>"`
- `"Thread not found"`
- `"Access denied"`
- `"Message not found"`
- `"Attachment not found"`

---

## Security Considerations

1. **Authentication**: All endpoints require user authentication
2. **Access Control**: Users can only access threads they are participants of
3. **Attachment Security**: Attachments use access tokens for secure downloads
4. **CSRF**: CSRF protection is disabled for API endpoints (`csrf=False`)

---

## Models

### messaging.thread
- `name`: Thread name
- `partner_ids`: Participants (Many2many)
- `message_ids`: Messages in thread (One2many)
- `thread_type`: Type (sms, chat, group)
- `last_message_date`: Last message timestamp

### messaging.message
- `thread_id`: Parent thread
- `author_id`: Message author
- `body`: Message content
- `message_type`: Type (sms, text)
- `attachment_ids`: Attached files (Many2many)
- `phone_number`: For SMS messages
- `sms_status`: SMS delivery status
- `is_read`: Read status

---

## Support

For issues and feature requests, please contact your system administrator.

## License

This module is licensed under LGPL-3.

## Author

Your Company

## Version

17.0.1.0.0

# Messaging API - Postman Testing Guide

## Base Configuration

**Base URL:** `http://localhost:8069`
**Database:** `odoo2`
**Login:** `admin@gmail.com`
**Password:** `123456`

---

## Authentication (Required First)

### Login to Get Session Cookie

**Method:** POST
**URL:** `http://localhost:8069/web/session/authenticate`
**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "db": "odoo2",
    "login": "admin@gmail.com",
    "password": "123456"
  },
  "id": 1
}
```

**Success Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "uid": 3,
    "is_system": true,
    "is_admin": true,
    "user_context": {...},
    "db": "odoo2",
    "server_version": "17.0",
    "session_id": "your_session_id_here"
  }
}
```

**Important:** Save the `session_id` from the response. You'll need to include it in a cookie for all subsequent requests.

**In Postman:**
1. After login, go to **Cookies** (below Send button)
2. Find the `session_id` cookie
3. All subsequent requests will automatically use this cookie

---

## 📱 Messaging APIs

### 1. Get All Threads

**Method:** POST
**URL:** `http://localhost:8069/api/messaging/threads`
**Headers:**
```
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body (raw JSON):**
```json
{
  "jsonrpc": "2.0",
  "params": {}
}
```

**Optional - Filter by Type:**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "thread_type": "chat"
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "threads": [
      {
        "id": 1,
        "name": "Test Chat Group",
        "type": "group",
        "participants": [
          {
            "id": 3,
            "name": "Administrator"
          }
        ],
        "last_message": "Hello! This is a test message.",
        "last_message_date": "2025-12-03 06:20:50",
        "unread_count": 0
      }
    ]
  }
}
```

---

### 2. Create New Thread

**Method:** POST
**URL:** `http://localhost:8069/api/messaging/thread/create`
**Headers:**
```
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body (raw JSON):**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "name": "My New Chat",
    "thread_type": "group"
  }
}
```

**With Participants:**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "name": "Team Discussion",
    "partner_ids": [3, 5, 7],
    "thread_type": "group"
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "success": true,
    "thread_id": 1,
    "name": "My New Chat"
  }
}
```

---

### 3. Send Message

**Method:** POST
**URL:** `http://localhost:8069/api/messaging/message/send`
**Headers:**
```
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body (raw JSON):**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "thread_id": 1,
    "body": "Hello! This is my message."
  }
}
```

**With Attachments:**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "thread_id": 1,
    "body": "Check out this document!",
    "attachment_ids": [85, 86]
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "success": true,
    "message_id": 1,
    "created_date": "2025-12-03 06:20:50"
  }
}
```

---

### 4. Get Messages from Thread

**Method:** POST
**URL:** `http://localhost:8069/api/messaging/messages`
**Headers:**
```
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body (raw JSON):**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "thread_id": 1,
    "limit": 50,
    "offset": 0
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "messages": [
      {
        "id": 1,
        "author_id": 3,
        "author_name": "Administrator",
        "body": "Hello! This is a test message from the API.",
        "message_type": "text",
        "is_read": false,
        "created_date": "2025-12-03 06:20:50",
        "attachments": []
      }
    ],
    "thread_id": 1,
    "thread_name": "Test Chat Group"
  }
}
```

---

### 5. Mark Message as Read

**Method:** POST
**URL:** `http://localhost:8069/api/messaging/message/read`
**Headers:**
```
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body (raw JSON) - Single Message:**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "message_id": 1
  }
}
```

**Multiple Messages:**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "message_ids": [1, 2, 3, 4]
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "success": true,
    "marked_count": 4
  }
}
```

---

### 6. Get Unread Count

**Method:** POST
**URL:** `http://localhost:8069/api/messaging/unread/count`
**Headers:**
```
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body (raw JSON):**
```json
{
  "jsonrpc": "2.0",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "unread_count": 5,
    "unread_by_thread": [
      {
        "thread_id": 1,
        "thread_name": "Test Chat Group",
        "unread_count": 3
      },
      {
        "thread_id": 2,
        "thread_name": "+1234567890",
        "unread_count": 2
      }
    ]
  }
}
```

---

## 📎 Attachment APIs

### 7. Upload Attachment

**Method:** POST
**URL:** `http://localhost:8069/api/messaging/attachment/upload`
**Headers:**
```
Cookie: session_id=YOUR_SESSION_ID
```
**Note:** Do NOT set Content-Type header - Postman will set it automatically for form-data

**Body (form-data):**
- Key: `file` | Type: File | Value: (select your file)
- Key: `name` | Type: Text | Value: `my_document.pdf`
- Key: `thread_id` | Type: Text | Value: `1` (optional)

**Response:**
```json
{
  "success": true,
  "attachment_id": 85,
  "name": "my_document.pdf",
  "mimetype": "application/pdf",
  "file_size": 1024000,
  "access_token": false
}
```

---

### 8. Download Attachment

**Method:** GET
**URL:** `http://localhost:8069/api/messaging/attachment/85`
**Headers:**
```
Cookie: session_id=YOUR_SESSION_ID
```

**With Access Token (optional):**
**URL:** `http://localhost:8069/api/messaging/attachment/85?access_token=abc123`

**Response:** Binary file download

---

### 9. Get Attachment Info

**Method:** POST
**URL:** `http://localhost:8069/api/messaging/attachment/info/85`
**Headers:**
```
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body (raw JSON):**
```json
{
  "jsonrpc": "2.0",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "id": 85,
    "name": "test_document.txt",
    "mimetype": "text/plain",
    "file_size": 18,
    "url": "http://localhost:8069/api/messaging/attachment/85",
    "access_token": false,
    "create_date": "2025-12-03 06:21:41"
  }
}
```

---

### 10. Delete Attachment

**Method:** POST
**URL:** `http://localhost:8069/api/messaging/attachment/delete/85`
**Headers:**
```
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body (raw JSON):**
```json
{
  "jsonrpc": "2.0",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "success": true,
    "attachment_id": 85
  }
}
```

---

## 📱 SMS APIs

### 11. Send SMS

**Method:** POST
**URL:** `http://localhost:8069/api/messaging/sms/send`
**Headers:**
```
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body (raw JSON):**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "phone_number": "+1234567890",
    "message": "Hello from Odoo SMS API!"
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "success": true,
    "message_id": 2,
    "sms_id": 1,
    "status": "sent"
  }
}
```

**Note:** Status will be "error" if SMS provider is not configured in Odoo.

---

### 12. Receive SMS (Webhook)

**Method:** POST
**URL:** `http://localhost:8069/api/messaging/sms/receive`
**Headers:**
```
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body (raw JSON):**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "phone_number": "+1234567890",
    "message": "Incoming SMS message"
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "success": true,
    "message_id": 3
  }
}
```

---

### 13. Get SMS Threads

**Method:** POST
**URL:** `http://localhost:8069/api/messaging/sms/threads`
**Headers:**
```
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body (raw JSON):**
```json
{
  "jsonrpc": "2.0",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "threads": [
      {
        "id": 2,
        "name": "+1234567890",
        "phone_number": "+1234567890",
        "last_message": "Hello from Odoo SMS API!",
        "last_message_date": "2025-12-03 06:21:58",
        "unread_count": 0
      }
    ]
  }
}
```

---

### 14. Get SMS Status

**Method:** POST
**URL:** `http://localhost:8069/api/messaging/sms/status/2`
**Headers:**
```
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body (raw JSON):**
```json
{
  "jsonrpc": "2.0",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "message_id": 2,
    "status": "sent",
    "phone_number": "+1234567890",
    "sent_date": "2025-12-03 06:21:58"
  }
}
```

---

## 🔍 Search & Discovery APIs

### 15. Search Partners

**Method:** POST
**URL:** `http://localhost:8069/api/messaging/partners/search`
**Headers:**
```
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body (raw JSON):**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "query": "admin",
    "limit": 20
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "partners": [
      {
        "id": 3,
        "name": "Administrator",
        "email": "admin@gmail.com",
        "phone": false,
        "mobile": false
      }
    ]
  }
}
```

---

### 16. Get Thread Participants

**Method:** POST
**URL:** `http://localhost:8069/api/messaging/thread/participants/1`
**Headers:**
```
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body (raw JSON):**
```json
{
  "jsonrpc": "2.0",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "thread_id": 1,
    "thread_name": "Test Chat Group",
    "participants": [
      {
        "id": 3,
        "name": "Administrator",
        "email": "admin@gmail.com",
        "phone": false
      }
    ]
  }
}
```

---

### 17. Add Thread Participant

**Method:** POST
**URL:** `http://localhost:8069/api/messaging/thread/add_participant`
**Headers:**
```
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body (raw JSON):**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "thread_id": 1,
    "partner_id": 5
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "success": true,
    "thread_id": 1,
    "partner_id": 5
  }
}
```

---

## 🔧 Postman Setup Instructions

### Setting Up in Postman

1. **Create New Collection**
   - Name it "Odoo Messaging API"

2. **Add Environment Variables**
   - Go to Environments → Create new environment
   - Add variables:
     - `base_url`: `http://localhost:8069`
     - `db`: `odoo2`
     - `login`: `admin@gmail.com`
     - `password`: `123456`
     - `session_id`: (leave empty, will be set after login)

3. **First Request - Authentication**
   - Create a new POST request for authentication
   - In Tests tab, add this script to automatically save session_id:
   ```javascript
   var jsonData = pm.response.json();
   if (jsonData.result && jsonData.result.session_id) {
       pm.environment.set("session_id", jsonData.result.session_id);
   }
   ```

4. **Use Variables in Requests**
   - URL: `{{base_url}}/api/messaging/threads`
   - Cookie: `session_id={{session_id}}`

5. **Create Folders**
   - Authentication
   - Messaging APIs
   - Attachment APIs
   - SMS APIs
   - Search & Discovery

---

## Common Error Responses

### Authentication Error
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": 200,
    "message": "Odoo Server Error",
    "data": {
      "name": "odoo.exceptions.AccessDenied",
      "message": "Access Denied"
    }
  }
}
```

### Missing Parameters
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "error": "thread_id and body are required"
  }
}
```

### Not Found
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "error": "Thread not found"
  }
}
```

### Access Denied
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "error": "Access denied"
  }
}
```

---

## Tips for Testing

1. **Always authenticate first** - Run the authentication request before any other API calls

2. **Check cookies** - Make sure the session_id cookie is being sent with each request

3. **Save IDs** - After creating threads, messages, or uploading files, save their IDs for testing other endpoints

4. **Test sequence:**
   - Authenticate
   - Create thread
   - Send message
   - Get messages
   - Upload attachment
   - Send message with attachment

5. **For mobile apps** - Store the session_id securely and include it in all requests

6. **Session expiry** - If you get authentication errors, re-authenticate to get a fresh session

---

## Complete Testing Flow Example

```
1. POST /web/session/authenticate
   → Get session_id

2. POST /api/messaging/thread/create
   → Get thread_id (e.g., 1)

3. POST /api/messaging/message/send
   Body: {"thread_id": 1, "body": "First message"}
   → Get message_id

4. POST /api/messaging/attachment/upload
   Upload a file
   → Get attachment_id (e.g., 85)

5. POST /api/messaging/message/send
   Body: {"thread_id": 1, "body": "With attachment", "attachment_ids": [85]}

6. POST /api/messaging/messages
   Body: {"thread_id": 1}
   → See all messages including attachments

7. POST /api/messaging/threads
   → See your thread with unread count

8. POST /api/messaging/message/read
   Body: {"message_ids": [1, 2]}
   → Mark messages as read

9. POST /api/messaging/unread/count
   → Verify unread count decreased
```

---

## 📥 Import Postman Collection (JSON)

Save this as `messaging_api.postman_collection.json` and import into Postman:

```json
{
  "info": {
    "name": "Odoo Messaging API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"jsonrpc\": \"2.0\",\n  \"method\": \"call\",\n  \"params\": {\n    \"db\": \"odoo2\",\n    \"login\": \"admin@gmail.com\",\n    \"password\": \"123456\"\n  },\n  \"id\": 1\n}"
            },
            "url": {
              "raw": "http://localhost:8069/web/session/authenticate",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8069",
              "path": ["web", "session", "authenticate"]
            }
          }
        }
      ]
    },
    {
      "name": "Messaging",
      "item": [
        {
          "name": "Get Threads",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"jsonrpc\": \"2.0\",\n  \"params\": {}\n}"
            },
            "url": {
              "raw": "http://localhost:8069/api/messaging/threads",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8069",
              "path": ["api", "messaging", "threads"]
            }
          }
        },
        {
          "name": "Create Thread",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"jsonrpc\": \"2.0\",\n  \"params\": {\n    \"name\": \"My Chat\",\n    \"thread_type\": \"group\"\n  }\n}"
            },
            "url": {
              "raw": "http://localhost:8069/api/messaging/thread/create",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8069",
              "path": ["api", "messaging", "thread", "create"]
            }
          }
        },
        {
          "name": "Send Message",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"jsonrpc\": \"2.0\",\n  \"params\": {\n    \"thread_id\": 1,\n    \"body\": \"Hello World!\"\n  }\n}"
            },
            "url": {
              "raw": "http://localhost:8069/api/messaging/message/send",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8069",
              "path": ["api", "messaging", "message", "send"]
            }
          }
        },
        {
          "name": "Get Messages",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"jsonrpc\": \"2.0\",\n  \"params\": {\n    \"thread_id\": 1,\n    \"limit\": 50\n  }\n}"
            },
            "url": {
              "raw": "http://localhost:8069/api/messaging/messages",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8069",
              "path": ["api", "messaging", "messages"]
            }
          }
        }
      ]
    }
  ]
}
```

---

## Support

For issues or questions about the API, refer to the README.md file in the module directory.

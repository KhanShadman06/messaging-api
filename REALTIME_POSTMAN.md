# Real-Time APIs - Postman Quick Reference

## Base Configuration
- **Base URL:** `http://localhost:8069`
- **Database:** `odoo2`
- **Login:** `admin@gmail.com`
- **Password:** `123456`

**Don't forget to authenticate first!**

---

## 📡 Long Polling APIs

### 1. Poll for New Messages (Long Polling)

**Wait for new messages in a specific chat**

```
POST http://localhost:8069/api/messaging/poll/messages
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body:**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "thread_id": 1,
    "last_message_id": 5,
    "timeout": 30
  }
}
```

**Response (with new messages):**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "has_new": true,
    "count": 2,
    "messages": [
      {
        "id": 6,
        "author_id": 5,
        "author_name": "John Doe",
        "body": "New message!",
        "message_type": "text",
        "is_read": false,
        "created_date": "2025-12-03 10:30:15",
        "attachments": []
      }
    ]
  }
}
```

**Response (timeout - no new messages):**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "has_new": false,
    "count": 0,
    "messages": []
  }
}
```

---

### 2. Poll for All Updates

**Monitor all chats for new messages**

```
POST http://localhost:8069/api/messaging/poll/updates
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body:**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "timeout": 30
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "has_updates": true,
    "unread_count": 5,
    "threads_with_updates": [
      {
        "thread_id": 1,
        "thread_name": "Chat with John",
        "unread_count": 3,
        "last_message": "Hey there!",
        "last_message_date": "2025-12-03 10:30:45"
      }
    ]
  }
}
```

---

## 🔔 Notification APIs

### 3. Get Notification Count

```
POST http://localhost:8069/api/messaging/notifications/count
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body:**
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
    "total_count": 12,
    "by_type": {
      "chat": 8,
      "group": 3,
      "sms": 1
    }
  }
}
```

---

### 4. Mark All as Read

**Mark all messages in a thread as read:**
```
POST http://localhost:8069/api/messaging/notifications/mark_all_read
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body (specific thread):**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "thread_id": 1
  }
}
```

**Body (all threads):**
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
    "marked_count": 12
  }
}
```

---

## ⌨️ Typing Indicator APIs

### 5. Start Typing

```
POST http://localhost:8069/api/messaging/typing/start
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body:**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "thread_id": 1
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
    "partner_id": 3
  }
}
```

---

### 6. Stop Typing

```
POST http://localhost:8069/api/messaging/typing/stop
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body:**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "thread_id": 1
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
    "partner_id": 3
  }
}
```

---

### 7. Get Typing Status

```
POST http://localhost:8069/api/messaging/typing/status/1
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body:**
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
    "typing_users": []
  }
}
```

---

## 👤 Presence / Online Status APIs

### 8. Update Your Presence

**Call this every 2-5 minutes to stay "online"**

```
POST http://localhost:8069/api/messaging/presence/update
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body:**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "status": "online"
  }
}
```

**Status options:** `"online"`, `"away"`, `"offline"`

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "success": true,
    "partner_id": 3,
    "status": "online"
  }
}
```

---

### 9. Check Online Status

**Check if your chat partners are online**

```
POST http://localhost:8069/api/messaging/presence/status
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

**Body:**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "partner_ids": [5, 7, 9]
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "presence": [
      {
        "partner_id": 5,
        "name": "John Doe",
        "status": "online",
        "last_seen": "2025-12-03 10:35:22"
      },
      {
        "partner_id": 7,
        "name": "Jane Smith",
        "status": "offline",
        "last_seen": "2025-12-03 09:15:10"
      }
    ]
  }
}
```

---

## 🧪 Testing Scenarios in Postman

### Scenario 1: Test Long Polling

1. **Tab 1:** Start long polling
   ```json
   POST /api/messaging/poll/messages
   {
     "jsonrpc": "2.0",
     "params": {
       "thread_id": 1,
       "last_message_id": 0,
       "timeout": 60
     }
   }
   ```
   *This will wait up to 60 seconds*

2. **Tab 2:** Send a message
   ```json
   POST /api/messaging/message/send
   {
     "jsonrpc": "2.0",
     "params": {
       "thread_id": 1,
       "body": "Test message!"
     }
   }
   ```

3. **Tab 1:** Should return immediately with the new message!

---

### Scenario 2: Test Notifications

1. **Get current count:**
   ```json
   POST /api/messaging/notifications/count
   {"jsonrpc": "2.0", "params": {}}
   ```
   → Shows: `"total_count": 0`

2. **Send a message** (as different user or in new thread)

3. **Get count again:**
   ```json
   POST /api/messaging/notifications/count
   {"jsonrpc": "2.0", "params": {}}
   ```
   → Shows: `"total_count": 1`

4. **Mark as read:**
   ```json
   POST /api/messaging/notifications/mark_all_read
   {"jsonrpc": "2.0", "params": {}}
   ```

5. **Check count:**
   → Shows: `"total_count": 0`

---

### Scenario 3: Test Typing Indicators

1. **Start typing:**
   ```json
   POST /api/messaging/typing/start
   {"jsonrpc": "2.0", "params": {"thread_id": 1}}
   ```

2. **Check status:**
   ```json
   POST /api/messaging/typing/status/1
   {"jsonrpc": "2.0", "params": {}}
   ```

3. **Stop typing:**
   ```json
   POST /api/messaging/typing/stop
   {"jsonrpc": "2.0", "params": {"thread_id": 1}}
   ```

---

### Scenario 4: Test Presence

1. **Update your status:**
   ```json
   POST /api/messaging/presence/update
   {"jsonrpc": "2.0", "params": {"status": "online"}}
   ```

2. **Check someone's status:**
   ```json
   POST /api/messaging/presence/status
   {"jsonrpc": "2.0", "params": {"partner_ids": [3]}}
   ```
   → Should show "online" if last activity < 5 minutes

3. **Wait 6 minutes without activity**

4. **Check again:**
   → Should show "offline"

---

## 🔥 Real-World Testing Flow

### Simulating Two Users Chatting

**User A (you):**
1. Authenticate as admin@gmail.com
2. Create thread: `thread_id = 1`
3. Start long polling on thread 1

**User B (second Postman tab or Insomnia):**
1. Authenticate as different user
2. Join thread 1
3. Send message

**User A:**
→ Long poll immediately returns with new message!

---

## ⚡ Performance Testing

### Test Long Poll Timeout

```json
POST /api/messaging/poll/messages
{
  "jsonrpc": "2.0",
  "params": {
    "thread_id": 1,
    "timeout": 5
  }
}
```

**Expected:**
- Request takes ~5 seconds
- Returns: `{"has_new": false, "messages": []}`

---

### Test Multiple Concurrent Polls

Open 3 tabs in Postman, all polling the same thread:

**Tab 1, 2, 3:**
```json
POST /api/messaging/poll/messages
{
  "jsonrpc": "2.0",
  "params": {
    "thread_id": 1,
    "timeout": 30
  }
}
```

**Tab 4:** Send message

**Result:** All 3 tabs should return immediately with the message!

---

## 💡 Tips for Postman

1. **Use Collections**
   - Create "Real-Time APIs" collection
   - Group by category (Polling, Notifications, etc.)

2. **Save Responses**
   - Save example responses for documentation
   - Use for comparing expected vs actual

3. **Use Pre-request Scripts**
   ```javascript
   // Auto-update timestamp
   pm.environment.set("timestamp", new Date().toISOString());
   ```

4. **Use Tests**
   ```javascript
   // Verify response time
   pm.test("Response time < 5s", () => {
     pm.expect(pm.response.responseTime).to.be.below(5000);
   });

   // Verify structure
   pm.test("Has result", () => {
     pm.expect(pm.response.json().result).to.exist;
   });
   ```

5. **Environment Variables**
   - `{{base_url}}` = `http://localhost:8069`
   - `{{thread_id}}` = `1`
   - `{{session_id}}` = (from login)

---

## 🐛 Common Issues

### Request Hangs Forever
- **Check timeout:** Max is 60 seconds
- **Check thread_id:** Must exist and you must be a participant

### 400 Bad Request
- **Check JSON format:** Must be valid JSON
- **Check Content-Type:** Must be `application/json`
- **Check authentication:** Cookie must be valid

### Empty Responses
- **Check last_message_id:** Should be ID of last message you have
- **No new messages:** Wait for timeout or send a test message

---

## 📊 All Real-Time Endpoints

| # | Endpoint | Purpose | Timeout |
|---|----------|---------|---------|
| 1 | `/api/messaging/poll/messages` | Long poll for new messages | Yes (30-60s) |
| 2 | `/api/messaging/poll/updates` | Poll for all chat updates | Yes (30-60s) |
| 3 | `/api/messaging/notifications/count` | Get unread count | No |
| 4 | `/api/messaging/notifications/mark_all_read` | Mark as read | No |
| 5 | `/api/messaging/typing/start` | Start typing | No |
| 6 | `/api/messaging/typing/stop` | Stop typing | No |
| 7 | `/api/messaging/typing/status/<id>` | Check who's typing | No |
| 8 | `/api/messaging/presence/update` | Update online status | No |
| 9 | `/api/messaging/presence/status` | Check online status | No |

---

## ✅ Complete Test Checklist

- [ ] Authenticate successfully
- [ ] Long poll returns on new message
- [ ] Long poll times out correctly
- [ ] Notification count updates
- [ ] Mark all as read works
- [ ] Typing start/stop works
- [ ] Presence update works
- [ ] Online status shows correctly
- [ ] All endpoints return valid JSON
- [ ] Error handling works

---

**Your API now has real-time capabilities!** 🚀

Test thoroughly and refer to REALTIME_GUIDE.md for implementation details.

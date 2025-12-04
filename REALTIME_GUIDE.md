# Real-Time Messaging Guide - Long Polling & Notifications

This guide explains how to implement real-time chat features using long polling, notifications, typing indicators, and presence status.

---

## 🚀 What's New

Your messaging API now supports:
- ✅ **Long Polling** for real-time message delivery
- ✅ **Notifications** for unread message counts
- ✅ **Typing Indicators** to show when someone is typing
- ✅ **Presence Status** to show who's online/offline

---

## 📡 Long Polling APIs

### 1. Poll for New Messages in a Thread

**Use Case:** User is in a chat screen, waiting for new messages

**Endpoint:** `POST /api/messaging/poll/messages`

**How it works:**
- Client calls this endpoint with the last message ID they have
- Server waits up to 30 seconds (configurable) for new messages
- Returns immediately if new messages arrive
- Returns empty if timeout reached with no new messages

**Request:**
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

**Parameters:**
- `thread_id` (required): ID of the thread to monitor
- `last_message_id` (optional): ID of last message client has (gets messages after this)
- `timeout` (optional): Seconds to wait (default 30, max 60)

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
        "body": "Hey! How's it going?",
        "message_type": "text",
        "is_read": false,
        "created_date": "2025-12-03 10:30:15",
        "attachments": []
      },
      {
        "id": 7,
        "author_id": 5,
        "author_name": "John Doe",
        "body": "Did you see my email?",
        "message_type": "text",
        "is_read": false,
        "created_date": "2025-12-03 10:30:45",
        "attachments": []
      }
    ]
  }
}
```

**Response (no new messages - timeout):**
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

### 2. Poll for All Updates (Chat List Screen)

**Use Case:** User is on chat list screen, waiting for notifications from any chat

**Endpoint:** `POST /api/messaging/poll/updates`

**How it works:**
- Monitors ALL threads user is part of
- Returns when unread count changes
- Perfect for updating chat list screen badge counts

**Request:**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "timeout": 30
  }
}
```

**Parameters:**
- `timeout` (optional): Seconds to wait (default 30, max 60)
- `last_check` (optional): Timestamp of last check (ISO format)

**Response (with updates):**
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
        "last_message": "Did you see my email?",
        "last_message_date": "2025-12-03 10:30:45"
      },
      {
        "thread_id": 3,
        "thread_name": "Team Group",
        "unread_count": 2,
        "last_message": "Meeting at 3pm",
        "last_message_date": "2025-12-03 10:25:00"
      }
    ]
  }
}
```

**Response (no updates):**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "has_updates": false,
    "unread_count": 0,
    "threads_with_updates": []
  }
}
```

---

## 🔔 Notification APIs

### 3. Get Notification Count

**Endpoint:** `POST /api/messaging/notifications/count`

**Request:**
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

**Use Case:** User clicks "Mark all as read" button

**Endpoint:** `POST /api/messaging/notifications/mark_all_read`

**Mark all in specific thread:**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "thread_id": 1
  }
}
```

**Mark ALL messages as read:**
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

**Use Case:** User starts typing in chat input field

**Endpoint:** `POST /api/messaging/typing/start`

**Request:**
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

**Use Case:** User stops typing (sent message or cleared input)

**Endpoint:** `POST /api/messaging/typing/stop`

**Request:**
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

### 7. Check Who's Typing

**Endpoint:** `POST /api/messaging/typing/status/1`

**Request:**
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

**Note:** Typing indicators are currently simplified. For production, implement with Redis/cache for persistent storage across requests.

---

## 👤 Presence / Online Status APIs

### 8. Update Your Presence

**Use Case:** Keep user shown as "online" by calling periodically

**Endpoint:** `POST /api/messaging/presence/update`

**Request:**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "status": "online"
  }
}
```

**Status Options:**
- `online` - User is active
- `away` - User is away
- `offline` - User went offline

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

**Use Case:** Show if chat partner is online

**Endpoint:** `POST /api/messaging/presence/status`

**Request:**
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
      },
      {
        "partner_id": 9,
        "name": "Bob Wilson",
        "status": "online",
        "last_seen": "2025-12-03 10:36:01"
      }
    ]
  }
}
```

**Logic:** User is considered "online" if last activity was within 5 minutes.

---

## 📱 Mobile App Implementation

### Chat Screen (Individual Conversation)

```javascript
class ChatScreen {
  constructor(threadId) {
    this.threadId = threadId;
    this.lastMessageId = 0;
    this.isPolling = false;
  }

  // Start long polling when user opens chat
  startLongPolling() {
    this.isPolling = true;
    this.pollForMessages();
  }

  // Stop when user leaves chat
  stopLongPolling() {
    this.isPolling = false;
  }

  async pollForMessages() {
    while (this.isPolling) {
      try {
        const response = await fetch('/api/messaging/poll/messages', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Cookie': `session_id=${sessionId}`
          },
          body: JSON.stringify({
            jsonrpc: "2.0",
            params: {
              thread_id: this.threadId,
              last_message_id: this.lastMessageId,
              timeout: 30
            }
          })
        });

        const data = await response.json();

        if (data.result.has_new) {
          // New messages arrived!
          this.displayNewMessages(data.result.messages);

          // Update last message ID
          const messages = data.result.messages;
          if (messages.length > 0) {
            this.lastMessageId = messages[messages.length - 1].id;
          }
        }

        // Continue polling
      } catch (error) {
        console.error('Polling error:', error);
        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, 5000));
      }
    }
  }

  displayNewMessages(messages) {
    messages.forEach(msg => {
      // Add message to UI
      this.addMessageToUI(msg);

      // Play notification sound if from other user
      if (msg.author_id !== currentUserId) {
        this.playNotificationSound();
      }
    });
  }

  // Typing indicator
  onTyping() {
    // User started typing
    fetch('/api/messaging/typing/start', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': `session_id=${sessionId}`
      },
      body: JSON.stringify({
        jsonrpc: "2.0",
        params: {
          thread_id: this.threadId
        }
      })
    });

    // Clear previous timeout
    clearTimeout(this.typingTimeout);

    // Auto-stop after 3 seconds of no typing
    this.typingTimeout = setTimeout(() => {
      this.onStopTyping();
    }, 3000);
  }

  onStopTyping() {
    fetch('/api/messaging/typing/stop', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': `session_id=${sessionId}`
      },
      body: JSON.stringify({
        jsonrpc: "2.0",
        params: {
          thread_id: this.threadId
        }
      })
    });
  }

  // Check partner's online status
  async checkOnlineStatus(partnerId) {
    const response = await fetch('/api/messaging/presence/status', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': `session_id=${sessionId}`
      },
      body: JSON.stringify({
        jsonrpc: "2.0",
        params: {
          partner_ids: [partnerId]
        }
      })
    });

    const data = await response.json();
    const status = data.result.presence[0].status;

    // Update UI
    this.updateOnlineIndicator(status);
  }
}

// Usage
const chat = new ChatScreen(threadId);
chat.startLongPolling();

// When user leaves screen
// chat.stopLongPolling();
```

---

### Chat List Screen (All Conversations)

```javascript
class ChatListScreen {
  constructor() {
    this.isPolling = false;
  }

  startPolling() {
    this.isPolling = true;
    this.pollForUpdates();
  }

  stopPolling() {
    this.isPolling = false;
  }

  async pollForUpdates() {
    while (this.isPolling) {
      try {
        const response = await fetch('/api/messaging/poll/updates', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Cookie': `session_id=${sessionId}`
          },
          body: JSON.stringify({
            jsonrpc: "2.0",
            params: {
              timeout: 30
            }
          })
        });

        const data = await response.json();

        if (data.result.has_updates) {
          // Update badge counts
          this.updateBadgeCounts(data.result.threads_with_updates);

          // Show notification
          this.showNotification(
            `${data.result.unread_count} new messages`
          );
        }

      } catch (error) {
        console.error('Polling error:', error);
        await new Promise(resolve => setTimeout(resolve, 5000));
      }
    }
  }

  updateBadgeCounts(threadsWithUpdates) {
    threadsWithUpdates.forEach(thread => {
      // Update UI badge for each thread
      const badge = document.querySelector(`#thread-${thread.thread_id} .badge`);
      if (badge) {
        badge.textContent = thread.unread_count;
        badge.style.display = 'block';
      }
    });
  }

  // Background presence updates (every 2 minutes)
  startPresenceHeartbeat() {
    setInterval(() => {
      fetch('/api/messaging/presence/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Cookie': `session_id=${sessionId}`
        },
        body: JSON.stringify({
          jsonrpc: "2.0",
          params: {
            status: "online"
          }
        })
      });
    }, 120000); // Every 2 minutes
  }
}

// Usage
const chatList = new ChatListScreen();
chatList.startPolling();
chatList.startPresenceHeartbeat();
```

---

## 🔄 Real-Time Flow Diagram

```
USER A                          SERVER                       USER B
  |                               |                            |
  | 1. Open chat screen           |                            |
  |------------------------------>|                            |
  |                               |                            |
  | 2. Start long polling         |                            |
  | /poll/messages (wait 30s)     |                            |
  |------------------------------>|                            |
  |          (waiting...)         |                            |
  |                               |                            |
  |                               | 3. Send message            |
  |                               |<---------------------------|
  |                               |                            |
  | 4. Poll returns immediately!  |                            |
  |<------------------------------|                            |
  | (new message data)            |                            |
  |                               |                            |
  | 5. Display message            |                            |
  | 6. Start new poll             |                            |
  |------------------------------>|                            |
  |          (waiting...)         |                            |
```

---

## ⚡ Performance Tips

### 1. Connection Management
```javascript
// Don't create multiple polling connections
// Use one connection per screen

// WRONG ❌
setInterval(() => {
  pollForMessages(); // Creates new connection every 5 seconds
}, 5000);

// RIGHT ✅
async function continuousPolling() {
  while (isActive) {
    await pollForMessages(); // Reuses connection
  }
}
```

### 2. Timeout Settings
```javascript
// Short timeout for active chat screen
{
  "thread_id": 1,
  "timeout": 30  // 30 seconds
}

// Longer timeout for background updates
{
  "timeout": 60  // 60 seconds (max)
}
```

### 3. Battery Optimization
```javascript
// On mobile, adjust polling based on app state

// App in foreground - aggressive polling
const foregroundTimeout = 30;

// App in background - longer intervals
const backgroundTimeout = 60;

// App inactive - stop polling
if (appState === 'inactive') {
  stopPolling();
}
```

---

## 🐛 Troubleshooting

### Long Poll Not Returning
**Problem:** Poll endpoint hangs and never returns

**Solutions:**
1. Check timeout parameter (max 60 seconds)
2. Verify thread_id exists and user has access
3. Check server logs for errors
4. Test with shorter timeout first (5-10 seconds)

### Missing Messages
**Problem:** Some messages don't appear in real-time

**Solutions:**
1. Verify `last_message_id` is correct
2. Check if polling loop restarts after each response
3. Ensure you're updating `last_message_id` after each poll

### High Server Load
**Problem:** Too many connections to server

**Solutions:**
1. Use `/poll/updates` instead of multiple `/poll/messages` calls
2. Implement connection pooling
3. Add exponential backoff on errors
4. Stop polling when screen is not visible

---

## 🚀 Production Recommendations

For production deployment, consider:

1. **Use Redis** for typing indicators and presence
2. **Implement WebSockets** for even better real-time performance
3. **Add rate limiting** to prevent abuse
4. **Use message queues** (RabbitMQ/Kafka) for scalability
5. **Add retry logic** with exponential backoff
6. **Monitor connection counts** and server load
7. **Implement circuit breakers** for failed connections

---

## 📊 API Endpoints Summary

| Endpoint | Purpose | Timeout | Use When |
|----------|---------|---------|----------|
| `/poll/messages` | Get new messages in one thread | 30s (max 60s) | User in chat screen |
| `/poll/updates` | Get updates across all threads | 30s (max 60s) | User in chat list |
| `/notifications/count` | Get unread counts | Instant | On app launch |
| `/notifications/mark_all_read` | Mark as read | Instant | User clicks "clear all" |
| `/typing/start` | User typing | Instant | Input field changes |
| `/typing/stop` | User stopped | Instant | Input cleared/sent |
| `/typing/status/<id>` | Check who's typing | Instant | Periodic check |
| `/presence/update` | Update online status | Instant | Every 2-5 minutes |
| `/presence/status` | Check online status | Instant | Chat screen open |

---

## ✅ Testing Checklist

- [ ] Long polling returns new messages immediately
- [ ] Long polling times out after specified duration
- [ ] Multiple users can chat in real-time
- [ ] Unread counts update correctly
- [ ] Typing indicators work (start/stop)
- [ ] Online status updates every 2-5 minutes
- [ ] App handles network errors gracefully
- [ ] Polling stops when user leaves screen
- [ ] Battery usage is acceptable on mobile
- [ ] Server can handle expected concurrent connections

---

Your messaging API now has **real-time capabilities**! 🎉

For questions or issues, refer to the main README.md or check server logs.

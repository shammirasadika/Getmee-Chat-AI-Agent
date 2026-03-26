# Database Tables Overview

This document describes the main tables in the GetMee Chatbot backend database.

## Table List

- `chat_sessions`: Stores each chat session (start/end time, user info, etc.)
- `chat_messages`: Stores every message exchanged in a session (user and bot messages)
- `feedback`: Legacy table for general feedback (kept for backward compatibility)
- `message_feedback`: Stores feedback on individual chatbot messages
- `session_feedback`: Stores feedback for the entire chat session
- `support_requests`: Legacy table for support requests (kept for backward compatibility)
- `support_tickets`: Stores support tickets created by users or escalation

## Table Details

### chat_sessions
- One row per chat session
- Columns: id (UUID), user_id, started_at, ended_at, status, ...

### chat_messages
- One row per message (user or bot)
- Columns: id (UUID), session_id (FK), sender, content, timestamp, ...

### feedback (legacy)
- General feedback (old system)
- Columns: id, user_id, message, rating, created_at, ...

### message_feedback
- Feedback on individual messages
- Columns: id, message_id (FK), user_id, rating, comment, created_at, ...

### session_feedback
- Feedback for the whole session
- Columns: id, session_id (FK), user_id, rating, comment, created_at, ...

### support_requests (legacy)
- Old support request records
- Columns: id, user_id, message, status, created_at, ...

### support_tickets
- New support ticket system
- Columns: id, session_id (FK), user_id, issue, status, created_at, ...

---

**Note:**
New feedback and support flows use `message_feedback`, `session_feedback`, and `support_tickets` only. Foreign keys (FK) link messages to sessions, feedback to messages/sessions, and tickets to sessions.

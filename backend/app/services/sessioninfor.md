# Session Information

This document describes the structure and contents of session records stored by the Redis Session Service in the backend.

## Overview
Session data is managed in Redis using multiple keys, all prefixed with `session:{session_key}:`. Each key stores a different aspect of the session state. All session keys use a Time-To-Live (TTL) to ensure automatic expiration of stale sessions.

## Session Keys and Their Contents

### 1. `:context`
Stores session metadata and runtime state as a JSON object. Example fields:
- `session_id`: Unique session identifier
- `user_email`: User's email address (if available)
- `preferred_language`: Language code (default: "en")
- `active`: Boolean, whether the session is active
- `last_intent`: Last detected user intent
- `waiting_for_feedback`: Boolean, if waiting for feedback
- `waiting_for_support_confirmation`: Boolean, if waiting for support confirmation
- `session_feedback_pending`: Boolean, if session feedback is pending
- `chat_status`: Status string (e.g., "active")

### 2. `:messages`
A list of recent message objects (JSON-serialized), representing the chat history for context. The number of messages is capped (see `MAX_RECENT_MESSAGES`).

### 3. `:feedback_state`
Tracks feedback for the latest bot response. Example fields:
- `last_bot_message_id`: ID of the last bot message
- `feedback_required`: Boolean, if feedback is required
- `feedback_submitted`: Boolean, if feedback has been submitted

### 4. `:support_state`
Manages escalation flow after negative feedback. Example fields:
- `not_satisfied_selected`: Boolean, if user selected not satisfied
- `support_confirmation_pending`: Boolean, if support confirmation is pending
- `selected_message_id`: ID of the message related to support

### 5. `:endchat_state`
Tracks end-of-chat and session feedback status. Example fields:
- `chat_ended`: Boolean, if the chat has ended
- `session_feedback_pending`: Boolean, if session feedback is pending

## Expiry
All session keys are set with a TTL (default: 1800 seconds) to ensure sessions are cleaned up automatically.

---

**Location:**
- Session management code: `backend/app/services/redis_session_service.py`

**See also:**
- Chat service logic: `backend/app/services/chat_service.py`
- Feedback and support flows: `backend/app/services/feedback_service.py`, `backend/app/services/message_service.py`

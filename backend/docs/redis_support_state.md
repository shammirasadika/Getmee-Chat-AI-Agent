# Redis-based Support State Tracking

## Overview
This system extends the support/chat escalation flow to use Redis for robust, session-scoped support state tracking, while preserving all existing RAG/fallback/escalation logic and PostgreSQL persistence.

## Features
- **Every support request submission is tracked in Redis** under the session key.
- **Repeat support submissions in the same session are prevented**: If a support request has already been submitted, the API blocks further submissions and returns a suitable message.
- **Support submission state is reviewable**: The chatbot can query Redis to check if support was already submitted, and retrieve the associated email and state.
- **No changes to core RAG/fallback/escalation logic or database persistence.**

## Redis Keys Used
- `session:{session_key}:support_state` — Tracks support flow state (e.g., not_satisfied_selected, support_confirmation_pending, selected_message_id).
- `session:{session_key}:context` — Now includes `support_request_sent` and `support_email` fields after support submission.

## API/Service Changes
- **Support Submission API** (`submit_support_request`):
  - Checks Redis for `support_request_sent` before processing.
  - On first submission, sets `support_request_sent=True` and stores support email in Redis context.
  - Prevents repeat submissions in the same session.
- **ChatService**:
  - New helper: `get_support_submission_state(session_key)` returns support submission state and email from Redis.

## Example Usage
- To check if support was already submitted for a session:
  ```python
  state = await chat_service.get_support_submission_state(session_key)
  if state["support_request_sent"]:
      # Inform user support is already submitted
  ```

## Compatibility
- All changes are additive and backward-compatible.
- No changes to RAG/fallback/escalation or PostgreSQL logic.

---
For further details, see the implementation in `backend/app/api/routes/support.py` and `backend/app/services/chat_service.py`.

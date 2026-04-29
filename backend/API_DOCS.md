# Backend API Documentation

## API Request Attribute Reference

### Quick Reference Table

| API Request              | Main Attributes                                      |
|-------------------------|-----------------------------------------------------|
| MessageFeedbackRequest  | session_key, message_id, feedback                    |
| SessionFeedbackRequest  | session_key, rating, comment                         |
| EndChatRequest          | session_key                                          |
| TryAgainRequest         | session_key                                          |
| SupportSubmitRequest    | session_id, user_email, user_message, language, source|
| ContactSupportRequest   | session_key, user_email, issue_summary, source        |
| ChatRequest             | message, session_id, language, unsatisfied_click, recontact_confirmed, recontact_declined |

Refer to the detailed descriptions below for attribute meanings.

This section explains the request attributes for each main API endpoint.

### MessageFeedbackRequest
Submitted when a user clicks Satisfied / Not Satisfied on a bot answer.
- **session_key**: `str` — Unique session identifier (e.g., "abc123")
- **message_id**: `str` — ID of the bot message being rated
- **feedback**: `str` — "satisfied" or "not_satisfied"

### SessionFeedbackRequest
Submitted when a user rates the whole conversation at end of chat.
- **session_key**: `str` — Unique session identifier
- **rating**: `int` — 1 to 5 star rating
- **comment**: `Optional[str]` — Optional user comment

### EndChatRequest
Marks the chat as ended.
- **session_key**: `str` — Unique session identifier

### TryAgainRequest
Resets support escalation state after user retries.
- **session_key**: `str` — Unique session identifier

### SupportSubmitRequest
Submit a support request after the user provides their email.
- **session_id**: `str` — Unique session identifier
- **user_email**: `EmailStr` — User's email address
- **user_message**: `str` — User's support message
- **language**: `Optional[str]` — Language code (default "en")
- **source**: `Optional[str]` — Source of escalation (e.g., "rag_fallback", "user_unsatisfied")

### ContactSupportRequest
Create a support ticket after user confirms they want human help.
- **session_key**: `str` — Unique session identifier
- **user_email**: `Optional[str]` — User's email (optional)
- **issue_summary**: `Optional[str]` — Short summary of the issue (auto-derived if empty)
- **source**: `Optional[str]` — Escalation source

### ChatRequest
Main chat endpoint for user messages.
- **message**: `str` — User's chat message
- **session_id**: `str` — Unique session identifier
- **language**: `Optional[str]` — Language code (e.g., "en")
- **unsatisfied_click**: `Optional[bool]` — If user clicked "not satisfied"
- **recontact_confirmed**: `bool` — If user confirmed recontact
- **recontact_declined**: `bool` — If user declined recontact

This document describes the main backend API endpoints, their purpose, and usage for the Getmee Chat AI Agent backend.

---

## 1. Feedback API (`/api/feedback`)


### POST `/api/feedback/message`
- **Purpose:** Record Satisfied / Not Satisfied feedback for a specific bot message. If "not_satisfied", the response includes `show_support_options=true` so the frontend can present Try Again / Contact Support.
- **Request Body:** `MessageFeedbackRequest` (includes `session_key`, `message_id`, `feedback`)
- **Response:** `MessageFeedbackResponse` (includes `success`, `feedback`, `show_support_options`)

### POST `/api/feedback/session`
- **Purpose:** Record a 1–5 star rating for the whole conversation.
- **Request Body:** `SessionFeedbackRequest`
- **Response:** `SessionFeedbackResponse`



### POST `/api/support/`
- **Purpose:** Submit a support request after user provides their email. Prevents repeat submissions, builds chat summary, and triggers fallback escalation.
- **Request Body:** `SupportSubmitRequest` (includes `session_id`, `user_message`, `user_email`, `language`, etc.)
- **Response:** `SupportSubmitResponse` (includes `success`, `message`, `request_id`)
---

### POST `/api/feedback/contact-support`
- **Purpose:** Create a support ticket after user confirms they want human help. Also updates session email if provided and saves to support_requests for escalation tracking.
- **Request Body:** `ContactSupportRequest` (includes `session_key`, `user_email`, `issue_summary`, etc.)
- **Response:** `ContactSupportResponse` (includes `success`, `ticket_id`, `detail`)


## 3. Chat API (`/api/chat`)

### POST `/api/chat/`
- **Purpose:** Main chat endpoint. Handles user chat requests and returns bot responses.
- **Request Body:** `ChatRequest`
- **Response:** `ChatResponse`



## 5. Health API (`/api/health`)

### GET `/api/health/`
- **Purpose:** Basic health check. Returns `{ "status": "ok" }` if the service is running.

### GET `/api/health/ready`
- **Purpose:** Readiness check. Returns `{ "ready": true }` if the service is ready to accept traffic.

### GET `/api/health/db-check`
- **Purpose:** Checks the status of Redis, PostgreSQL, and ChromaDB connections. Returns their status as `ok` or `error`.


## Notes
- All endpoints return JSON responses.
- For detailed request/response schemas, see the FastAPI Swagger UI at `/docs` or the OpenAPI spec at `/openapi.json`.
- Authentication and rate limiting are not described here; see backend code for details if implemented.

## Notes
- All endpoints return JSON responses.
- For detailed request/response schemas, see the FastAPI Swagger UI at `/docs` or the OpenAPI spec at `/openapi.json`.
- Authentication and rate limiting are not described here; see backend code for details if implemented.

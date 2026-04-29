# Backend API Documentation

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

### POST `/api/feedback/end-chat`  <!-- Not in use, keep for future -->
- **Purpose:** Mark the chat as ended and signal that session feedback should be shown.  
- **Request Body:** `EndChatRequest`
- **Response:** `EndChatResponse`

### POST `/api/feedback/try-again`  <!-- Not in use, keep for future -->
- **Purpose:** User chose Try Again after Not Satisfied — resets support state.  
- **Request Body:** `TryAgainRequest`
- **Response:** `TryAgainResponse`


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

# GetMee Chatbot Backend - System Flow

## Escalation to Human Support (Fallback)

When the knowledge base cannot find relevant information for a user query, the backend enforces a **strict fallback** - no LLM-generated answers are allowed. Instead, the system saves a support request in PostgreSQL, checks Redis cooldown, and sends an email notification to staff.

### Fallback Escalation Flow

```mermaid
graph TD
    F1[User submits query]
    F2[Backend retrieves from ChromaDB]
    F3{Relevant documents found?}
    F4[Generate RAG answer via LLM]
    F5[Return strict fallback message]
    F6[Save support request in PostgreSQL]
    F7{Redis cooldown active?}
    F8[Send email to support team]
    F9[Set Redis cooldown key - 5 min TTL]
    F10[Skip email - cooldown active]
    F11[Return response with fallback_used=true]
    F12[Staff receives email and follows up]

    F1 --> F2 --> F3
    F3 -->|YES| F4
    F3 -->|NO| F5
    F5 --> F6
    F6 --> F7
    F7 -->|NO| F8
    F8 --> F9
    F9 --> F11
    F7 -->|YES| F10
    F10 --> F11
    F8 --> F12
```

### Data Storage Architecture

```mermaid
graph LR
    subgraph Temporary_Redis
        R1[Session chat history]
        R2[Email cooldown keys]
        R3[Context/working memory]
    end

    subgraph Permanent_PostgreSQL
        P1[support_requests table]
        P2[feedback table]
        P3[chat_logs table]
    end

    subgraph Notification
        E1[Email to support team]
    end

    P1 --- E1
```

| Component | Purpose | Data Lifetime |
|-----------|---------|---------------|
| Redis | Session memory, cooldown flags | Temporary (TTL-based) |
| PostgreSQL | Support requests, feedback, logs | Permanent |
| Email | Staff notification | One-time trigger |

### PostgreSQL support_requests Table

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Auto-increment ID |
| session_id | VARCHAR | User session identifier |
| user_message | TEXT | The user's original question |
| fallback_message | TEXT | The fallback response returned |
| language | VARCHAR(10) | Detected language code |
| status | VARCHAR(20) | Request status (default: pending) |
| email_sent | BOOLEAN | Whether email notification was sent |
| chat_summary | TEXT | Recent chat context (nullable) |
| created_at | TIMESTAMP | When the request was created |

---

## User Flow

```mermaid
graph TD
    U1[User visits chat interface]
    U2[User types message in any supported language]
    U3[User submits message]
    U4[Frontend sends POST /api/chat to backend]
    U5[Backend processes request]
    U6{Relevant documents found?}
    U7[Return RAG answer with sources]
    U8[Return fallback message + escalate to support]
    U9[Frontend displays response]
    U10[Frontend shows support options if fallback_used=true]

    U1 --> U2 --> U3 --> U4 --> U5 --> U6
    U6 -->|YES| U7 --> U9
    U6 -->|NO| U8 --> U9
    U9 --> U10
```

---

## Chat Request Flow (Detailed)

```mermaid
graph TD
    A[User sends POST /api/chat] --> B[API Route - chat.py]
    B --> C[ChatService]
    C --> D[LanguageService: Detect language]
    C --> E[RetrievalService: Query ChromaDB]
    E --> F{Distance below threshold?}
    F -->|YES| G[Extract and filter meaningful chunks]
    G --> H{Relevant chunks found?}
    H -->|YES| I[PromptService: Build RAG prompt]
    I --> J[LLMClient: Generate response]
    J --> K[Validate language purity]
    K --> L[SessionService: Save turn to Redis]
    L --> M[Return answer + sources]

    F -->|NO| N[Try fallback language retrieval]
    H -->|NO| N
    N --> O{Fallback has relevant chunks?}
    O -->|YES| I
    O -->|NO| P[Return strict fallback message]
    P --> Q[SupportService: Save to PostgreSQL]
    Q --> R{Redis cooldown active?}
    R -->|NO| S[Send email notification]
    S --> T[Set cooldown in Redis]
    R -->|YES| U[Skip email]
    T --> L
    U --> L
```

---

## Feedback Flow

```mermaid
graph TD
    A[User sends POST /api/feedback] --> B[API Route - feedback.py]
    B --> C[FeedbackService]
    C --> D[PostgresClient: Save feedback]
    D --> E[API returns success]
```

## Escalation Flow

```mermaid
graph TD
    A[User sends POST /api/escalation] --> B[API Route - escalation.py]
    B --> C[ChatService: Handle escalation]
    C --> D[API returns escalation status]
```

## Health Check Flow

```mermaid
graph TD
    A[User sends GET /api/health or /api/ready] --> B[API Route - health.py]
    B --> C[API returns status]
```

---

## Supported Languages

The system supports 10 languages with auto-detection and translated fallback messages:

en, es, ar, fr, zh, pt, de, ja, ko, hi

---

- All services are modular and can be extended or replaced.
- ChromaDB, Redis, and PostgreSQL integrations are abstracted for easy upgrades.
- Language detection and prompt building ensure correct language output.
- **Strict fallback policy**: the LLM is never called when no relevant documents are found.
- **PostgreSQL is the source of truth** for all support request records.
- **Redis handles only temporary data**: sessions, cooldowns, working memory.
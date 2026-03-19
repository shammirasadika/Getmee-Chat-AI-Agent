# GetMee Chatbot Backend – System Flow

## Escalation to Human Support (Fallback)

If the knowledge base cannot find relevant information for a user query, the backend will escalate the request to human support. For example, it can send an email to a staff member (e.g., shammirasadika123@gmail.com) with the user’s question and session details.

### Escalation Flow Example

```mermaid
graph TD
    F1[User submits query]
    F2[Backend cannot find relevant knowledge]
    F3[Backend triggers escalation]
    F4[Send email to staff (ex :shammirasadika123@gmail.com)]
    F5[Staff receives email and follows up]
    F1 --> F2 --> F3 --> F4 --> F5
```

The user will be notified that their request has been forwarded to human support for further assistance.

## User Flow

```mermaid
graph TD
    U1[User visits chat interface (frontend/app)]
    U2[User types message in English or Spanish]
    U3[User submits message]
    U4[Frontend sends POST /api/chat to backend]
    U5[Backend processes request (see Chat Request Flow)]
    U6[Backend returns answer, language, sources, fallback]
    U7[Frontend displays chatbot response in correct language]
    U1 --> U2 --> U3 --> U4 --> U5 --> U6 --> U7
```

# GetMee Chatbot Backend – System Flow

## Chat Request Flow

```mermaid
graph TD
    A[User sends POST /api/chat] --> B[API Route (chat.py)]
    B --> C[ChatService]
    C --> D[LanguageService: Detect language]
    C --> E[RetrievalService: Query ChromaDB]
    C --> F[PromptService: Build prompt]
    C --> G[LLMClient: Generate response]
    C --> H[SessionService: Save turn]
    G --> I[ChatService: Compose response]
    I --> J[API returns answer, language, sources, fallback]
```

## Feedback Flow

```mermaid
graph TD
    A[User sends POST /api/feedback] --> B[API Route (feedback.py)]
    B --> C[FeedbackService]
    C --> D[PostgresClient: Save feedback]
    D --> E[API returns success]
```

## Escalation Flow

```mermaid
graph TD
    A[User sends POST /api/escalation] --> B[API Route (escalation.py)]
    B --> C[ChatService: Handle escalation]
    C --> D[API returns escalation status]
```

## Health Check Flow

```mermaid
graph TD
    A[User sends GET /api/health or /api/ready] --> B[API Route (health.py)]
    B --> C[API returns status]
```

---

- All services are modular and can be extended or replaced.
- ChromaDB, Redis, and PostgreSQL integrations are abstracted for easy future upgrades.
- Language detection and prompt building ensure correct language output.

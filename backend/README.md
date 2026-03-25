# GetMee Chatbot Backend (MVP)

This is the backend for the GetMee Chatbot MVP. It is a FastAPI-based service that supports Retrieval-Augmented Generation (RAG) using a local ChromaDB knowledge base. The backend supports multilingual queries and responses across 10 languages.

## Features
- FastAPI backend with modular structure
- Chat endpoint with auto language detection (en, es, ar, fr, zh, pt, de, ja, ko, hi)
- Retrieval from local ChromaDB (path configurable via env)
- **Strict fallback escalation** — no hallucinated answers when the knowledge base has no relevant data
- **PostgreSQL** for permanent storage of support requests, feedback, and chat logs
- **Redis** for session memory, recent chat context, and email cooldown logic
- **Email notification** to support team on fallback escalation (with anti-spam cooldown)
- Multilingual fallback retrieval (cross-language search with automatic translation)
- Health and readiness endpoints
- Docker-friendly design

## Fallback Escalation Flow

When the chatbot cannot find a relevant answer in the vector database:

1. **No LLM generation** — the system does NOT allow the LLM to generate a general or assumed answer
2. **Fixed fallback response** — returns a predefined message in the user's language:
   > "I couldn't find a relevant answer to your question. Your enquiry will be assigned to our support team. Please be patient while we assist you."
3. **PostgreSQL record** — saves the support request (session_id, message, language, status, timestamps)
4. **Redis cooldown check** — prevents duplicate email notifications from the same session (5-minute cooldown)
5. **Email notification** — sends an HTML email to the configured support email address
6. **Response flags** — returns `fallback_used: true` in the API response

### Architecture Rules
| Component | Role |
|-----------|------|
| **ChromaDB** | Vector database for document retrieval |
| **Redis** | Session memory, recent chat history, email cooldown (temporary data only) |
| **PostgreSQL** | Permanent storage for support requests, feedback, chat logs |
| **Email** | Notification mechanism only (not primary storage) |

## Folder Structure
```
backend/
  app/
    main.py
    api/
      routes/
        chat.py
        feedback.py
        escalation.py
        health.py
    core/
      config.py
      email_config.py
      logging.py
      prompts.py
    models/
      chat.py
      feedback.py
      common.py
    services/
      chat_service.py        # Main chat logic with strict fallback
      retrieval_service.py    # ChromaDB retrieval + distance threshold
      language_service.py     # Language detection + fallback messages (10 languages)
      prompt_service.py       # RAG prompt builder
      session_service.py      # Redis session management
      feedback_service.py     # PostgreSQL feedback storage
      support_service.py      # Fallback escalation (PostgreSQL + Redis + Email)
    clients/
      chroma_client.py        # ChromaDB vector search
      llm_client.py           # Groq LLM integration
      redis_client.py         # Redis client with cooldown support
      postgres_client.py      # PostgreSQL client with support_requests
      email_client.py         # SMTP email client
    utils/
      exceptions.py
      helpers.py
  tests/
  requirements.txt
  .env.example
  Dockerfile
  README.md
```

## Local Development

1. **Install dependencies**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables**
   Copy `.env.example` to `.env` and set:
   ```env
   # Required
   GROQ_API_KEY=your_groq_api_key
   LLM_PROVIDER=groq

   # PostgreSQL (Neon or local)
   POSTGRES_URL=postgresql://user:password@localhost:5432/getmee

   # Redis (Upstash or local)
   REDIS_URL=redis://localhost:6379/0

   # ChromaDB
   CHROMA_HOST=localhost
   CHROMA_PORT=8000
   CHROMA_COLLECTION=getmee_docs_dev

   # Support email notification
   SUPPORT_EMAIL=support@yourcompany.com
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   MAIL_FROM=your_email@gmail.com
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587

   # Fallback behavior
   ALLOW_GENERAL_FALLBACK=false
   SUPPORT_EMAIL_COOLDOWN=300
   ```

3. **Start ChromaDB server**
   ```bash
   chroma run --path ./ingestion_pipeline/chroma-data
   ```

4. **Run the server**
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8001
   ```

5. **API Docs**
   Visit [http://localhost:8001/docs](http://localhost:8001/docs)

## API Endpoints

### POST `/api/chat`
Request:
```json
{
  "message": "How can I reset my password?",
  "session_id": "abc123",
  "language": "en"
}
```

**Successful RAG response:**
```json
{
  "answer": "To reset your password, go to Settings > Security...",
  "language": "en",
  "sources": [{"text": "..."}],
  "fallback_used": false,
  "retrieval_language": "en"
}
```

**Fallback response (no relevant data found):**
```json
{
  "answer": "I couldn't find a relevant answer to your question. Your enquiry will be assigned to our support team. Please be patient while we assist you.",
  "language": "en",
  "sources": [],
  "fallback_used": true,
  "retrieval_language": "en"
}
```

### POST `/api/feedback`
Submit user feedback on a chat response.

### POST `/api/escalation`
Manually trigger escalation to human support.

### GET `/api/health`
Health check endpoint.

### GET `/api/ready`
Readiness check endpoint.

## Supported Languages
| Code | Language |
|------|----------|
| en | English |
| es | Spanish |
| ar | Arabic |
| fr | French |
| zh | Chinese |
| pt | Portuguese |
| de | German |
| ja | Japanese |
| ko | Korean |
| hi | Hindi |

## Notes
- This backend does **not** handle ingestion. Use the separate ingestion pipeline to populate ChromaDB.
- `ALLOW_GENERAL_FALLBACK=false` (default) ensures the LLM never generates assumed answers when no relevant documents are found.
- PostgreSQL is the source of truth for all support/fallback records. Redis is only for temporary session data and cooldown.
- Email is a notification mechanism — support requests are always saved in PostgreSQL first.

---

**Backend only. No frontend code included.**

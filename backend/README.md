# GetMee Chatbot Backend (MVP)

This is the backend for the GetMee Chatbot MVP. It is a FastAPI-based service that supports Retrieval-Augmented Generation (RAG) using a local ChromaDB knowledge base. The backend supports both English and Spanish queries and responses.

## Features
- FastAPI backend with modular structure
- Chat endpoint with language detection (English/Spanish)
- Retrieval from local ChromaDB (path configurable via env)
- Session memory (Redis, with fallback)
- Feedback endpoint (PostgreSQL, with placeholder)
- Escalation/fallback logic
- Health and readiness endpoints
- Docker-friendly design

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
      logging.py
    models/
      chat.py
      feedback.py
      common.py
    services/
      chat_service.py
      retrieval_service.py
      language_service.py
      prompt_service.py
      session_service.py
      feedback_service.py
    clients/
      chroma_client.py
      llm_client.py
      redis_client.py
      postgres_client.py
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
   - Copy `.env.example` to `.env` and update values as needed.

3. **Run the server**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **API Docs**
   - Visit [http://localhost:8000/docs](http://localhost:8000/docs)

## API Example

### POST `/api/chat`
Request:
```json
{
  "message": "Hola, necesito ayuda con la plataforma",
  "session_id": "abc123",
  "language": "es"
}
```
Response:
```json
{
  "answer": "Claro, te ayudo con eso...",
  "language": "es",
  "sources": [],
  "fallback_used": false
}
```

## Notes
- This backend does **not** handle ingestion. Use the separate ingestion pipeline to populate ChromaDB.
- LLM, Redis, and PostgreSQL integrations are placeholders for MVP.
- For production, add authentication, monitoring, and robust error handling.

---

**Backend only. No frontend code included.**

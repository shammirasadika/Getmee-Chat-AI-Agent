

# Backend Setup Instructions – GetMee Chatbot

## Deployment & Configuration Summary (DC)

- **LLM Provider:** Claude API (Anthropic). Add your Claude API key and endpoint to `.env` and configure the backend LLM client for Claude.
- **ChromaDB Collection:** Use `CHROMA_COLLECTION=getmee_docs_dev` in both ingestion and backend retrieval.
- **Email:** Use `shammirasadika123@` as both sender and receiver for escalation emails.
- **Session Memory:** Store 10 recent turns per session in Redis (temporary memory only).
- **Fallback Message:** Use a simple default: "Sorry, I couldn’t find an answer. Your request has been forwarded to support."
- **Deployment:** Backend API on Render, frontend on Vercel.
- **Security:** No authentication required for MVP.


**Best Practical Cloud Choices:**
- Use [Upstash](https://upstash.com/) (free tier, easy setup, serverless) for Redis
- Use [Neon](https://neon.tech/) (free tier, serverless, easy setup) for PostgreSQL
- For production email, use [FastAPI-Mail](https://fastapi-mail.readthedocs.io/)

## 1. Python Environment
- Create and activate a virtual environment:
  ```bash
  python -m venv .venv
  # On Windows:
  .venv\Scripts\activate
  # On Mac/Linux:
  source .venv/bin/activate
  ```
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

## 2. Environment Variables
- Copy `.env.example` to `.env` and update values as needed (ChromaDB path, Redis, PostgreSQL, LLM keys, etc).


## 3. PostgreSQL Setup (Best Practical Choice: Neon)

- **Recommended:**
  - Use [Neon](https://neon.tech/) (free tier, serverless, easy setup)
  - Create a project/database and get the connection string from the Neon dashboard.
  - Update `.env`:
    ```
    POSTGRES_URL=your_neon_postgres_connection_string
    ```

- **Alternatives:**
  - [Supabase](https://supabase.com/) (generous free tier)
  - [ElephantSQL](https://www.elephantsql.com/) (free tiny plan)
  - Local PostgreSQL install (see previous instructions if needed)


## 4. Redis Setup (Best Practical Choice: Upstash)

- **Recommended:**
  - Use [Upstash](https://upstash.com/) (free tier, easy setup, serverless)
  - Create a database and get the connection string from the Upstash dashboard.
  - Update `.env`:
    ```
    REDIS_URL=your_upstash_redis_connection_string
    ```

- **Alternatives:**
  - [Redis Cloud](https://redis.com/try-free/) (free tier)
  - Local Redis install (see previous instructions if needed)

## 5. ChromaDB (Best Practical Choice: Local for Now)

- **Recommended:**
  - Use local ChromaDB storage as created by your ingestion pipeline.
  - Set `CHROMA_PATH` in `.env` to the correct path (e.g., `../ingestion_pipeline/chroma-data`).
  - Cloud options for ChromaDB are not yet mature for free/production use. Revisit as the project grows.

## 6. Email Sending (Escalation)
- For production, use [FastAPI-Mail](https://fastapi-mail.readthedocs.io/) or `smtplib` for simple SMTP.
- Example with FastAPI-Mail:
  ```bash
  pip install fastapi-mail
  ```
  Configure mail settings in `.env`:
  ```
  MAIL_USERNAME=your_email@gmail.com
  MAIL_PASSWORD=your_password
  MAIL_FROM=your_email@gmail.com
  MAIL_PORT=587
  MAIL_SERVER=smtp.gmail.com
  MAIL_TLS=True
  MAIL_SSL=False
  ```

## 7. Running the Backend
- Start the FastAPI server:
  ```bash
  uvicorn app.main:app --reload
  ```
- Visit [http://localhost:8000/docs](http://localhost:8000/docs) for API documentation.

---

**Note:**
- For cloud DB/Redis, update connection strings accordingly.
- For email, use app passwords or OAuth for Gmail if 2FA is enabled.
- For any issues, check logs and verify all services are running.

# Deployment & Configuration Summary (DC)

- **LLM Provider:** Claude API (Anthropic). Add your Claude API key and endpoint to `.env` and configure the backend LLM client for Claude.
- **ChromaDB Collection:** Use `CHROMA_COLLECTION=getmee_docs_dev` in both ingestion and backend retrieval.
- **Email:** Use `shammirasadika123@` as both sender and receiver for escalation emails.
- **Session Memory:** Store 10 recent turns per session in Redis (temporary memory only).
- **Fallback Message:** Use a simple default: "Sorry, I couldn’t find an answer. Your request has been forwarded to support."
- **Deployment:** Backend API on Render, frontend on Vercel.
- **Security:** No authentication required for MVP.

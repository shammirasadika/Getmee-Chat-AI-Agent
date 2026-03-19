# Multilingual Fallback Retrieval Flow

## Overview

The RAG backend supports multilingual fallback retrieval. If no relevant results are found in the user's original language, the system automatically retries retrieval in an alternative language. The final answer is **always** returned in the user's selected language, regardless of which language the retrieval succeeded in.

---

## Flow Diagram

```
User sends: { message, session_id, language }
    │
    ▼
┌─────────────────────────────────┐
│ 1. Determine Language           │
│    - Use request.language        │
│    - Or auto-detect from message │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│ 2. Primary Retrieval            │
│    - Search ChromaDB with       │
│      original user query        │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│ 3. Check Retrieval Quality      │
│    - Are there documents?       │
│    - Is min distance < 1.5?     │
└─────────┬───────────┬───────────┘
          │           │
        YES          NO
          │           │
          ▼           ▼
┌──────────────┐  ┌──────────────────────────────┐
│ Build prompt │  │ 4. Fallback Retrieval         │
│ & generate   │  │    - Get fallback language     │
│ answer in    │  │      (en↔es)                   │
│ user lang    │  │    - Translate query via LLM   │
│              │  │    - Retry ChromaDB search     │
│ Response:    │  └──────────┬─────────┬───────────┘
│ fallback:    │             │         │
│   false      │           YES        NO
│ retrieval:   │             │         │
│   original   │             ▼         ▼
└──────────────┘  ┌──────────────┐  ┌──────────────────────┐
                  │ Build prompt │  │ 7. No Results         │
                  │ with cross-  │  │    Return safe        │
                  │ language     │  │    fallback message   │
                  │ context      │  │    in user's language │
                  │              │  │                       │
                  │ Generate     │  │ EN: "I could not find │
                  │ answer in    │  │  relevant information │
                  │ user lang    │  │  in the knowledge     │
                  │              │  │  base."               │
                  │ Response:    │  │                       │
                  │ fallback:    │  │ ES: "No pude encontrar│
                  │   true       │  │  información relevante│
                  │ retrieval:   │  │  en la base de        │
                  │   fallback   │  │  conocimiento."       │
                  └──────────────┘  └──────────────────────┘
```

---

## Key Rules

| Rule | Description |
|------|-------------|
| **Response language is fixed** | The final answer is ALWAYS in the user's selected language |
| **Retrieval language can change** | If primary fails, retrieval retries in the fallback language |
| **No language mixing** | The LLM prompt strictly forbids mixing languages in the answer |
| **Cross-language context is allowed** | The LLM may read context in any language for understanding, but must respond only in the user's language |

---

## Files Involved

| File | Role |
|------|------|
| `app/models/chat.py` | `ChatResponse` with `fallback_used` and `retrieval_language` fields |
| `app/services/language_service.py` | Language detection, fallback language map, fallback messages |
| `app/services/retrieval_service.py` | ChromaDB retrieval + `has_relevant_results()` quality check |
| `app/services/prompt_service.py` | Builds prompt with strict language-only instruction |
| `app/services/chat_service.py` | Orchestrates the full multilingual fallback flow |
| `app/clients/llm_client.py` | `generate()` for answers, `translate()` for fallback query translation |

---

## Response Schema

```json
{
  "answer": "string (always in user's language)",
  "language": "en | es",
  "sources": [{"text": "..."}],
  "fallback_used": true | false,
  "retrieval_language": "en | es (language retrieval succeeded in)"
}
```

---

## Examples

### Example 1: Spanish user, primary retrieval succeeds

```
Request:  { "message": "¿Cómo reseteo mi contraseña?", "language": "es" }
Retrieval: Spanish query → ChromaDB → relevant results found

Response: {
  "answer": "Para resetear tu contraseña, ve a configuración...",
  "language": "es",
  "fallback_used": false,
  "retrieval_language": "es"
}
```

### Example 2: Spanish user, fallback to English retrieval

```
Request:  { "message": "¿Cómo reseteo mi contraseña?", "language": "es" }
Retrieval: Spanish query → ChromaDB → no relevant results
Fallback:  Translate → "How do I reset my password?" → ChromaDB → results found

Response: {
  "answer": "Para resetear tu contraseña, ve a configuración...",  ← still Spanish
  "language": "es",
  "fallback_used": true,
  "retrieval_language": "en"  ← retrieval was in English
}
```

### Example 3: No results in any language

```
Request:  { "message": "¿Cuál es el clima hoy?", "language": "es" }
Retrieval: Spanish query → no results
Fallback:  English query → no results

Response: {
  "answer": "No pude encontrar información relevante en la base de conocimiento.",
  "language": "es",
  "fallback_used": true,
  "retrieval_language": "es"
}
```

---

## Distance Threshold

- ChromaDB returns `distances` for each result (lower = better match)
- Threshold: **1.5** (configurable in `retrieval_service.py`)
- If all distances ≥ 1.5, results are considered irrelevant → triggers fallback

## Supported Fallback Pairs

| User Language | Fallback Language |
|---------------|-------------------|
| English (en)  | Spanish (es)      |
| Spanish (es)  | English (en)      |

Additional pairs can be added in `language_service.py` → `FALLBACK_LANGUAGE_MAP`.

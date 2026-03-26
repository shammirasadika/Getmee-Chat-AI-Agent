# 2.2 Developed Components, Features, and Functions (Sprint 1 Report)

This section provides a detailed and accurate description of the components, features, and functions developed during Sprint 1 of the GetMee Customer Service Chat AI Agent project. The content reflects the actual implementation and current working setup of the system.

## 2.2.1 System Architecture and Technical Design

The chatbot system was designed as a modular and scalable architecture supporting an embeddable AI-powered customer service solution. The architecture separates frontend, backend, data storage, and AI components to ensure flexibility and maintainability.

- **React + TypeScript chatbot widget** (embeddable via JavaScript script)
- **FastAPI backend** acting as the orchestration layer
- **Redis (Upstash)** for session context handling
- **PostgreSQL (Neon)** for persistent storage
- **ChromaDB (local)** as the current vector database for RAG (not Pinecone)
- **Claude (Anthropic API)** for response generation
- **FastAPI ingestion service** for document processing

> **Note:** In the current implementation, the system runs with a locally configured ChromaDB instance for vector storage and retrieval, enabling development and testing without external dependencies. Pinecone is not used in Sprint 1.

**Architecture Flow:**
```
User → React Widget → FastAPI → Redis | PostgreSQL | ChromaDB → Claude
```

### Three-Layer Architecture
The system follows a three-layer architecture: Presentation Layer (React UI), Application Layer (FastAPI backend), and Data & Knowledge Layer (Redis, PostgreSQL, ChromaDB, and LLM).

### RAG Architecture
The system uses a Retrieval-Augmented Generation approach. Documents are processed through an ingestion pipeline, converted into embeddings, and stored in ChromaDB. During query execution, relevant chunks are retrieved and combined with the user query to generate accurate responses using the LLM.

---

## 2.2.2 Ingestion Pipeline (Backend Service)

A dedicated FastAPI-based ingestion pipeline was developed to process documents and populate the knowledge base.

- **POST /ingest endpoint**
- **Text extraction** (PDF, DOCX, TXT)
- **Text cleaning**
- **Chunking**
- **Embedding generation**
- **Storage in ChromaDB (local implementation)**

**Ingestion Flow:**
```
POST /ingest → extract_text → clean_text → chunk_text → embed_chunks → store_in_chromadb
```

At Sprint 1 completion, the ingestion pipeline is fully functional in a local environment using ChromaDB. This setup supports development and testing, while future deployment may involve cloud-based vector databases.

---

## 2.2.3 Chat Interface and Backend Skeleton

The chatbot interface and backend foundation were implemented to support core conversational functionality.

### React Chat Widget
A responsive React chatbot UI was developed and deployed as an embeddable widget using a JavaScript script.

### Backend (FastAPI)
The backend includes endpoints such as `/chat`, `/feedback`, and `/health`, which are implemented or stubbed. The `/escalate` endpoint is planned for future implementation.

### Session Handling (Redis)
Redis is used for temporary session management, storing context, messages, and interaction states with a 24-hour TTL.

### Persistent Storage
PostgreSQL is used as the main persistent database for storing chat sessions, messages, feedback, and support requests.

---

## Implementation Status Table
| Component              | Status                |
|------------------------|-----------------------|
| Chat UI scaffold       | Completed             |
| Backend structure      | Partially implemented |
| Session handling design| Completed             |
| Redis integration      | Partially implemented |
| Ingestion pipeline     | Completed (local)     |
| ChromaDB integration   | Completed (local)     |
| Pinecone integration   | Not used in Sprint 1  |
| API endpoints          | /chat, /feedback, /health implemented; /escalate planned |

---

**Summary**

Sprint 1 successfully established a working local RAG-based chatbot system with core architecture, ingestion pipeline, and chatbot interface implemented. The current setup uses ChromaDB (local) for vector storage, not Pinecone. All other components and flows described match the actual codebase as of Sprint 1 end (March 27, 2026).

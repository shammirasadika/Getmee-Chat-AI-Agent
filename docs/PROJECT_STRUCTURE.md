# Project Folder Structure Overview

This document explains the main folders and their purposes in the Getmee-Chat-AI-Agent project.

## Root Level
- **backend/**: Main backend application (API, business logic, models, services, configuration, and database files).
- **frontend/**: Main frontend application (React/TypeScript code, components, widgets, and static assets).
- **ingestion_pipeline/**: Handles data ingestion, processing, and ChromaDB integration.
- **Getmee-Chat-AI-Agent/**: Meta-folder containing backend, frontend, ingestion, and other project-wide code.
- **docker/**: Docker-related files for containerization.
- **README.md**: Project overview and setup instructions.

---

## backend/
- **api/**: API route definitions and logic.
**app/**: Main application code, with subfolders and key files:
  - **api/**: API route handlers.
  - **clients/**: External service clients.
  - **core/**: Core business logic and configuration. Notable files:
    - **config.py**: Loads and manages environment variables and application settings (e.g., database URLs, API keys, feature flags). Validates required config on startup.
    - **email_config.py**: Loads email server settings (username, password, server, port, TLS/SSL) from environment variables for sending emails.
    - **logging.py**: Sets up centralized logging configuration for the backend, formatting logs and directing them to stdout.
    - **prompts.py**: Stores prompt templates for LLM (Large Language Model) interactions, including system and user prompt rules for chat/answer generation.
  - **main.py**: FastAPI application entry point. Sets up the app, middleware, and includes API routers.
  - **models/**: Data models (e.g., Pydantic models for requests/responses).
  - **services/**: Service layer for business logic.
  - **utils/**: Utility/helper functions.
- **chroma-data/**: ChromaDB data files (e.g., chroma.sqlite3).
- **configuration/**: Backend configuration files.
- **docs/**: Backend documentation.
- **migrations/**: Database migration scripts.
- **tests/**: Backend tests.
- **utilities/**: Additional helper scripts.

---
## frontend/
- **src/**: Main source code (components, hooks, pages, etc.).
- **widget/**: Standalone chatbot widget code.
- **docs/**: Frontend documentation.
- **public/**: Static assets (e.g., robots.txt).
- **dist-widget/**: Built widget files.
- **Other config files**: (package.json, tsconfig, etc.)

---

## ingestion_pipeline/
- **chroma-data/**: ChromaDB data files.
- **config/**, **configuration/**: Ingestion config files.
- **docs/**: Ingestion documentation.
- **ingestion_pipeline/**: (subfolder, possibly for pipeline logic).
- **models/**, **pipeline/**, **routes/**, **services/**, **utils/**: Code for data processing, models, API routes, and utilities.

---

## docker/
- Docker configuration and test files for containerization.

---

## Top-level scripts
- **check_chroma_content.py, create_collection.py, reset_redis.py, view_redis.py**: Utility scripts for database and cache management.

---

For more details on any folder or file, see the respective README.md or docs/ folder inside each section.
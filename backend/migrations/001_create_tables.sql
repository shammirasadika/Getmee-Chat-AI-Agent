
# ──────────────────────────────────────────────
# 4. support_request
# Purpose: store user requests for human support and email handling status
# ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS support_request (
    id               UUID      PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id        UUID      NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_message      TEXT      NULL,
    user_email        VARCHAR   NULL,
    fallback_message  TEXT      NULL,
    language          VARCHAR   NULL,
    status            VARCHAR   NOT NULL DEFAULT 'pending',
    email_sent        BOOLEAN   NOT NULL DEFAULT FALSE,
    chat_summary      TEXT      NULL,
    source            VARCHAR   NULL,
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_support_request_session_id ON support_request(session_id);
CREATE INDEX IF NOT EXISTS idx_support_request_status ON support_request(status);
CREATE INDEX IF NOT EXISTS idx_support_request_source ON support_request(source);
-- ============================================================
-- GetMee Chat AI Agent — PostgreSQL Schema Migration
-- Version: 001
-- Description: Core tables for chat sessions, messages,
--              feedback, support tickets, and session ratings
-- ============================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ──────────────────────────────────────────────
-- 1. chat_sessions
-- Purpose: persistent record of each chat session
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS chat_sessions (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    session_key   VARCHAR     UNIQUE NOT NULL,
    user_email    VARCHAR     NULL,
    preferred_language VARCHAR NULL,
    status        VARCHAR     NOT NULL DEFAULT 'active',   -- active / ended / escalated
    started_at    TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at      TIMESTAMP   NULL,
    created_at    TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_key ON chat_sessions(session_key);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_status ON chat_sessions(status);

-- ──────────────────────────────────────────────
-- 2. chat_messages
-- Purpose: store every user and bot message permanently
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS chat_messages (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id    UUID        NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    message_type  VARCHAR     NOT NULL,        -- user / bot
    message_text  TEXT        NOT NULL,
    language      VARCHAR     NULL,
    fallback_used BOOLEAN     NOT NULL DEFAULT FALSE,
    source_type   VARCHAR     NULL,            -- kb / fallback / support
    created_at    TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);

-- ──────────────────────────────────────────────
-- 3. message_feedback
-- Purpose: response-level feedback (satisfied / not_satisfied)
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS message_feedback (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id    UUID        NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
    session_id    UUID        NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    feedback      VARCHAR     NOT NULL,        -- satisfied / not_satisfied
    created_at    TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_message_feedback_message_id ON message_feedback(message_id);
CREATE INDEX IF NOT EXISTS idx_message_feedback_session_id ON message_feedback(session_id);

-- ──────────────────────────────────────────────
-- 4. support_tickets
-- Purpose: escalation records when user requests human help
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS support_tickets (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id    UUID        NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    message_id    UUID        NULL REFERENCES chat_messages(id) ON DELETE SET NULL,
    user_email    VARCHAR     NULL,
    issue_summary TEXT        NOT NULL,
    status        VARCHAR     NOT NULL DEFAULT 'open',  -- open / in_progress / closed
    created_at    TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_support_tickets_session_id ON support_tickets(session_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_status ON support_tickets(status);

-- ──────────────────────────────────────────────
-- 5. session_feedback
-- Purpose: end-of-chat rating for the whole conversation
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS session_feedback (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id    UUID        NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    rating        INT         NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment       TEXT        NULL,
    created_at    TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_session_feedback_session_id ON session_feedback(session_id);

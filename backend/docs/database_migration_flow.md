## Using the Neon Console

You can also manage your database schema directly from the Neon web console:

1. Open your Neon project and launch the SQL editor/console.
2. Paste and run any SQL you want (e.g., `CREATE TABLE`, `ALTER TABLE`, `DROP TABLE`).
3. Changes take effect immediately in your database.

This is equivalent to running your migration SQL files locally—just a different interface. You do not need Alembic or any migration tool if you’re comfortable managing schema changes this way.

**Tips:**
- Always back up important data before running destructive commands (like `DROP TABLE`).
- Keep your migration SQL files for documentation and reproducibility, even if you run them manually in the console.
# Database Migration Flow & Common Commands

This document explains the typical migration workflow for the GetMee Chatbot backend and provides common commands for managing your database schema.

---

## Migration Workflow

1. **Edit/Create Migration Script**
   - Add or modify SQL files in `backend/migrations/` (e.g., `001_create_tables.sql`).
   - Each file should contain only the changes for that migration (create, alter, drop tables, etc).

2. **Apply Migration to Database**
   - Use a tool like `psql`, DBeaver, or your cloud provider's SQL console to run the migration SQL against your database.
   - Example (using psql):
     ```sh
     psql $DATABASE_URL -f backend/migrations/001_create_tables.sql
     ```

3. **Verify Migration**
   - Check your database (via GUI or SQL) to ensure tables/columns were created or updated as expected.
   - Example:
     ```sql
     \dt   -- list tables
     SELECT * FROM chat_sessions LIMIT 5;
     ```

4. **Test Application**
   - Run backend tests or start the app to confirm everything works with the new schema.

---

## Common Migration Commands

### 1. Apply a Migration (psql)
```sh
psql $DATABASE_URL -f backend/migrations/001_create_tables.sql
```

### 2. List All Tables (psql)
```sql
\dt
```

### 3. Show Table Schema (psql)
```sql
\d+ chat_sessions
```

### 4. View Table Data (psql)
```sql
SELECT * FROM chat_sessions LIMIT 10;
```

### 5. Rollback (Manual)
- If you need to undo a migration, create a new SQL file with the reverse changes (e.g., `DROP TABLE ...`).

---

## Tips
- Keep each migration file focused and incremental (one change per file).
- Always back up your data before running destructive migrations.
- Use a migration tool (like Alembic) for more complex workflows, but raw SQL is fine for simple cases.

---

**See also:**
- `backend/docs/database_tables.md` for table descriptions.

# Redis & Context Handling Flow (Simple Overview)

## Purpose
- **Redis**: Fast, temporary storage for active chat session state and flow flags.
- **PostgreSQL**: Permanent storage for all messages, feedback, and tickets.

## Redis Key Structure
- All keys use: `session:{session_key}:<state>`
- No legacy or inconsistent keys.

## What Goes in Redis?
- **Context**: Small session metadata (not full chat history)
- **Messages**: Only the most recent N messages (e.g., last 10–20)
- **Feedback State**: Flags for feedback flow
- **Support State**: Flags for escalation flow
- **End Chat State**: Flags for session end

## Example Redis Keys
- `session:abc123:context` — session metadata (JSON)
- `session:abc123:messages` — recent messages (list)
- `session:abc123:feedback_state` — feedback flags (JSON)
- `session:abc123:support_state` — support flags (JSON)
- `session:abc123:endchat_state` — end chat flags (JSON)

## TTL (Auto-Expire)
- All session keys auto-expire after 24 hours of inactivity.

## PostgreSQL Responsibilities
- Stores all permanent data: messages, feedback, tickets, session logs.
- Every message is saved here (not just in Redis).

## Typical Flow
1. **User sends message**
   - Save message in PostgreSQL
   - Push to Redis messages (trim to N)
2. **Bot responds**
   - Save bot message in PostgreSQL
   - Update feedback_state, context in Redis
3. **User gives feedback**
   - Save feedback in PostgreSQL
   - Update feedback_state, context in Redis
4. **User requests support**
   - Save support ticket in PostgreSQL
   - Update support_state in Redis
5. **Chat ends**
   - Update session status in PostgreSQL
   - Update endchat_state in Redis
   - Expire/clear Redis session keys

## Why This Design?
- **Fast**: Redis gives instant access to session state for active chats.
- **Clean**: No duplicate or legacy keys; everything is namespaced.
- **Reliable**: PostgreSQL is the source of truth for all history and analytics.
- **Scalable**: Old/inactive sessions are auto-removed from Redis.

---
This flow keeps your chatbot fast, reliable, and easy to maintain.

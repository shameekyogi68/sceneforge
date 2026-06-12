# SceneForge — Auth & Multi-Project Kiro Spec

## 1. Overview

This spec extends the base SceneForge RAG chatbot with:
- **Supabase Auth** — email/password signup and login
- **Multi-project support** — each user owns multiple isolated projects
- **Document management** — list and delete individual documents
- **Rate limiting** — 100 questions/day per user (free tier safe)
- **Three new frontend pages** — login.html, dashboard.html, project.html

**Prerequisite:** The base SceneForge spec must already be implemented. This spec only describes additions and changes.

**Total cost: $0** — Supabase free tier + Gemini free tier.

---

## 2. What Changes vs. Base Spec

| Area | Base Spec | This Spec |
|------|-----------|-----------|
| Identity | `project_id` string in localStorage | UUID from Supabase Auth |
| Projects | Single project per browser session | Multiple projects per user account |
| Frontend | `index.html` only | `login.html`, `dashboard.html`, `project.html` |
| Auth | None | JWT tokens via Supabase Auth |
| Rate limiting | None | 100 questions/day per user |
| Document deletion | Not supported | `DELETE /documents/{id}` endpoint |
| Project deletion | Deletes chunks only | Cascades via FK to all related data |

---

## 3. Database Schema Changes

### 3.1 Run in Supabase SQL Editor (additive — does not drop existing data)

```sql
-- Add user_id to projects table
ALTER TABLE projects ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);

-- Add status column to documents table
ALTER TABLE documents ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'processing';

-- Profiles table for rate limiting
CREATE TABLE IF NOT EXISTS profiles (
    id                  UUID REFERENCES auth.users(id) PRIMARY KEY,
    email               TEXT,
    questions_today     INT DEFAULT 0,
    last_question_date  DATE DEFAULT CURRENT_DATE,
    created_at          TIMESTAMP DEFAULT NOW()
);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    project_id  UUID REFERENCES projects(id) ON DELETE CASCADE,
    title       TEXT,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id                  BIGSERIAL PRIMARY KEY,
    conversation_id     UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role                TEXT,
    content             TEXT,
    sources             JSONB,
    created_at          TIMESTAMP DEFAULT NOW()
);
```

### 3.2 Enable Row Level Security

```sql
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
```

### 3.3 RLS Policies

```sql
DROP POLICY IF EXISTS "Users own their projects" ON projects;
CREATE POLICY "Users own their projects" ON projects
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users own their documents" ON documents;
CREATE POLICY "Users own their documents" ON documents
    USING (EXISTS (
        SELECT 1 FROM projects
        WHERE projects.id = documents.project_id
        AND projects.user_id = auth.uid()
    ));

DROP POLICY IF EXISTS "Users own their chunks" ON document_chunks;
CREATE POLICY "Users own their chunks" ON document_chunks
    USING (EXISTS (
        SELECT 1 FROM projects
        WHERE projects.id = document_chunks.project_id
        AND projects.user_id = auth.uid()
    ));

DROP POLICY IF EXISTS "Users own their conversations" ON conversations;
CREATE POLICY "Users own their conversations" ON conversations
    USING (EXISTS (
        SELECT 1 FROM projects
        WHERE projects.id = conversations.project_id
        AND projects.user_id = auth.uid()
    ));

DROP POLICY IF EXISTS "Users own their messages" ON messages;
CREATE POLICY "Users own their messages" ON messages
    USING (EXISTS (
        SELECT 1 FROM conversations
        JOIN projects ON projects.id = conversations.project_id
        WHERE conversations.id = messages.conversation_id
        AND projects.user_id = auth.uid()
    ));

DROP POLICY IF EXISTS "Users own their profiles" ON profiles;
CREATE POLICY "Users own their profiles" ON profiles
    USING (auth.uid() = id);
```

> **Run all SQL above in Supabase SQL Editor before touching any code.**

---

## 4. Updated File Structure

```
sceneforge/
├── backend/
│   ├── __init__.py
│   ├── main.py          # UPDATED — add auth + project + document endpoints
│   ├── auth.py          # NEW — signup, login, get_current_user, check_rate_limit
│   ├── rag.py           # unchanged from base spec
│   ├── memory.py        # unchanged
│   ├── models.py        # unchanged
│   └── config.py        # unchanged
├── frontend/
│   ├── login.html       # NEW
│   ├── dashboard.html   # NEW
│   └── project.html     # NEW (replaces index.html)
├── uploads/
├── .env
├── requirements.txt     # UPDATED — add slowapi
└── Dockerfile
```

---

## 5. Updated `requirements.txt`

Add this line to existing `requirements.txt`:

```
slowapi==0.1.9
```

---

## 6. New File: `backend/auth.py`

### Imports

```python
from supabase import create_client
from fastapi import HTTPException
from datetime import date
import backend.config as config
```

### Supabase client

```python
supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
```

### Functions

#### `signup(email: str, password: str) -> Any`
- Call `supabase.auth.sign_up({"email": email, "password": password})`
- On success, INSERT into `profiles`: `{id: user.id, email, questions_today: 0, last_question_date: date.today().isoformat()}`
- On exception, raise `HTTPException(400, str(e))`
- Return the full Supabase auth response

#### `login(email: str, password: str) -> Any`
- Call `supabase.auth.sign_in_with_password({"email": email, "password": password})`
- On exception, raise `HTTPException(401, "Invalid email or password")`
- Return the full Supabase auth response

#### `get_current_user(token: str) -> Any`
- Call `supabase.auth.get_user(token)`
- On exception, raise `HTTPException(401, "Invalid token")`
- Return `user.user`

#### `check_rate_limit(user_id: str) -> bool`
- Query `profiles` WHERE `id = user_id`
- If no profile found: return `True` (allow)
- If `last_question_date` ≠ today: UPDATE `questions_today=0, last_question_date=today`; return `True`
- If `questions_today >= 100`: return `False`
- Otherwise: UPDATE `questions_today = questions_today + 1`; return `True`
- Import `date` from `datetime` — do not forget this import

---

## 7. Updated `backend/main.py`

### New imports to add

```python
from backend.auth import signup, login, get_current_user, check_rate_limit
from fastapi import Depends, Header
from supabase import create_client
import backend.config as config
import uuid

supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
```

### Auth helper (inline, add near top of file)

```python
def get_token(authorization: str = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")
    return authorization.replace("Bearer ", "")
```

---

### New Endpoints

#### `POST /auth/signup`
- Query params: `email: str`, `password: str`
- Call `signup(email, password)`
- Return `{"access_token": result.session.access_token, "user_id": result.user.id}`

#### `POST /auth/login`
- Query params: `email: str`, `password: str`
- Call `login(email, password)`
- Return `{"access_token": result.session.access_token, "user_id": result.user.id}`

#### `GET /auth/me`
- Header: `Authorization: Bearer <token>`
- Call `get_current_user(token)`
- Return `{"id": user.id, "email": user.email}`

---

#### `POST /projects`
- Query param: `name: str`
- Header: `Authorization: Bearer <token>`
- Decode token → get `user.id`
- INSERT into `projects`: `{name, user_id: user.id}`
- Return `result.data[0]`

#### `GET /projects`
- Header: `Authorization: Bearer <token>`
- Decode token → get `user.id`
- SELECT from `projects` WHERE `user_id = user.id`
- Return `result.data`

#### `DELETE /projects/{project_id}`
- Header: `Authorization: Bearer <token>`
- Decode token → verify `projects.user_id = user.id`; if not found raise `404`
- DELETE from `projects` WHERE `id = project_id` (FK cascade handles documents, chunks, conversations, messages)
- Return `{"message": "Project deleted"}`

---

#### `POST /upload` (REPLACE existing)
- Form fields: `file: UploadFile`, `project_id: str`
- Header: `Authorization: Bearer <token>`
- Validate: `.pdf` extension, file size ≤ `MAX_FILE_SIZE_MB`
- Verify user owns `project_id` via `projects` table; raise `403` if not
- Save temp file to `/tmp/{project_id}_{filename}`
- INSERT into `documents`: `{project_id, filename, status: "processing"}`
- Call `process_and_store_pdf(temp_path, filename, project_id)` from `rag.py`
- Delete temp file in `finally` block
- Return `{"success": True, "document_id": doc_id, "chunks": chunk_count}`

#### `POST /ask` (REPLACE existing)
- Query params: `message: str`, `project_id: str`, `conversation_id: str = None`
- Header: `Authorization: Bearer <token>`
- Validate non-empty `message`
- Decode token → verify user owns project; raise `403` if not
- Call `check_rate_limit(user.id)`; if `False` raise `HTTPException(429, "Daily limit reached (100 questions). Come back tomorrow.")`
- If no `conversation_id`: INSERT into `conversations` `{project_id, title: message[:50]}`; use new `id`
- Call `get_project_memory(project_id)` and `answer_with_sources(message, project_id, memory)` from `rag.py`
- Call `save_conversation_memory(...)` from `memory.py`
- Return `{"answer": answer, "sources": sources, "conversation_id": conversation_id, "remaining_questions": <100 minus today's count>}`

#### `GET /documents/{project_id}`
- Header: `Authorization: Bearer <token>`
- Verify token (no ownership check needed — RLS handles it)
- SELECT from `documents` WHERE `project_id = project_id`
- Return `result.data`

#### `DELETE /documents/{document_id}`
- Header: `Authorization: Bearer <token>`
- Decode token → fetch document → verify project ownership; raise `403` if not
- DELETE from `documents` WHERE `id = document_id`
- Return `{"message": "Document deleted"}`

---

## 8. Frontend Pages

### 8.1 `frontend/login.html`

**Purpose:** Signup and login. Redirects to `dashboard.html` if already logged in.

**State:**
- `localStorage.token` — JWT access token
- `localStorage.userId` — Supabase user UUID

**On load:** If `localStorage.token` exists → `window.location.href = '/dashboard.html'`

**Login flow:**
1. POST to `/auth/login?email=...&password=...`
2. On `200`: store `token` and `userId` in localStorage → redirect to `dashboard.html`
3. On error: show error message in `#error` div

**Signup flow:**
1. POST to `/auth/signup?email=...&password=...`
2. Same storage + redirect as login
3. On error: show `error.detail` in `#error` div

**Toggle:** Single form switches between Login and Sign Up mode by changing button `onclick` and button label.

---

### 8.2 `frontend/dashboard.html`

**Purpose:** List all projects for logged-in user. Create or delete projects.

**Auth guard:** On load, if `localStorage.token` is absent → redirect to `login.html`

**On load:** Call `loadProjects()` — GET `/projects` with `Authorization` header

**Create project:**
1. Show modal with text input
2. POST to `/projects?name=...`
3. On success: close modal, reload project list

**Delete project:**
1. `confirm()` dialog
2. DELETE to `/projects/{project_id}`
3. On success: reload project list

**Open project:** `window.location.href = '/project.html?project_id={id}'`

**Logout:** Remove `localStorage.token` and `localStorage.userId` → redirect to `login.html`

**If `GET /projects` returns `401`:** Remove token → redirect to `login.html`

---

### 8.3 `frontend/project.html`

**Purpose:** Document upload + RAG chat for a single project.

**URL param:** `?project_id=<uuid>`

**Auth guard:** If `localStorage.token` absent or `project_id` absent → redirect to `login.html`

**State (JS variables only, no localStorage):**
- `conversationId` — null initially; set from first `/ask` response

**On load:**
1. `loadProject()` — GET `/projects`, find matching id, set heading
2. `loadDocuments()` — GET `/documents/{project_id}`

**Upload flow:**
1. File input `change` event
2. Build `FormData` with `file` and `project_id`
3. POST to `/upload` with `Authorization` header
4. On success: show alert, call `loadDocuments()`
5. On error: show `error.detail` in alert

**Delete document:**
1. `confirm()` dialog
2. DELETE to `/documents/{document_id}`
3. On success: call `loadDocuments()`

**Chat flow:**
1. User types → `sendMessage()`
2. Append user bubble to `#chatMessages`
3. Show typing indicator
4. POST to `/ask?message=...&project_id=...&conversation_id=...`
5. Remove indicator → append assistant bubble + source list
6. Update `conversationId` from response
7. Show `remaining_questions` in `#remainingQuestions`
8. On `429`: show daily limit message in chat bubble
9. Enter key triggers `sendMessage()`

**Logout:** Remove `localStorage.token` → redirect to `login.html`

---

## 9. API Summary

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/auth/signup` | None | Create account |
| POST | `/auth/login` | None | Login |
| GET | `/auth/me` | Bearer | Get current user |
| GET | `/projects` | Bearer | List user's projects |
| POST | `/projects` | Bearer | Create project |
| DELETE | `/projects/{id}` | Bearer | Delete project + cascade |
| GET | `/documents/{project_id}` | Bearer | List project documents |
| DELETE | `/documents/{id}` | Bearer | Delete one document |
| POST | `/upload` | Bearer | Upload + process PDF |
| POST | `/ask` | Bearer | RAG Q&A with rate limit |
| GET | `/health` | None | Liveness check |

---

## 10. Known Gotchas

| # | Issue | Fix |
|---|-------|-----|
| 1 | `check_rate_limit` uses `date` — must `from datetime import date` in `auth.py` | Add import explicitly |
| 2 | `/auth/signup` and `/auth/login` use query params not JSON body — frontend must use `?email=...&password=...` in the URL | Match fetch URL exactly |
| 3 | Supabase RLS blocks all reads if policies are missing — run ALL policy SQL before testing | Verify in Supabase Table Editor → Policies tab |
| 4 | `documents` table must already exist from base spec; this spec only ADDs `status` column | Do not re-CREATE the table |
| 5 | `project_id` in `project.html` is now a UUID (from Supabase), not a user-typed string — never hardcode or localStorage it | Always read from `URLSearchParams` |
| 6 | `DELETE /projects/{id}` only cascades if FK `ON DELETE CASCADE` is set on `documents`, `conversations` tables | Verify FK constraints in Supabase schema editor |
| 7 | `remaining_questions` in `/ask` response is approximate — compute as `100 - profile.questions_today` after incrementing | Fetch updated profile count or compute locally |
| 8 | Supabase Auth JWT tokens expire — frontend should handle `401` on any request by clearing token and redirecting to login | Add global fetch wrapper or per-response check |
| 9 | `frontend/project.html` fetches `GET /projects` to find the project name — for large project lists this is wasteful; acceptable for MVP | Optimize later with `GET /projects/{id}` endpoint |
| 10 | Serving HTML files: FastAPI does not auto-serve `login.html`, `dashboard.html`, `project.html` from `frontend/` unless `StaticFiles` is mounted | Add `app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")` in `main.py` |

---

## 11. Static File Serving (Required Addition to `main.py`)

Add this at the **bottom** of `main.py` (after all route definitions):

```python
from fastapi.staticfiles import StaticFiles

# Must be last — catch-all for frontend routes
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
```

This serves `login.html`, `dashboard.html`, and `project.html` at their respective paths. The `GET /` route from the base spec can be removed or kept — `StaticFiles` takes precedence for `.html` files.

---

## 12. Test Plan Additions

### `tests/test_auth.py`

- `test_signup_creates_profile` — mock Supabase auth, verify profile INSERT called
- `test_login_returns_token` — mock auth, verify token in response
- `test_get_current_user_invalid_token` — expect `401`
- `test_check_rate_limit_new_user` — no profile → returns `True`
- `test_check_rate_limit_resets_daily` — stale date → resets counter → returns `True`
- `test_check_rate_limit_exceeded` — `questions_today >= 100` → returns `False`

### `tests/test_api.py` additions

- `test_create_project_authenticated` — valid token → `200` with project data
- `test_create_project_no_token` → `401`
- `test_list_projects_empty` — new user → `[]`
- `test_delete_project_not_owner` → `404`
- `test_upload_wrong_project_owner` → `403`
- `test_ask_rate_limited` — mock `check_rate_limit` returning `False` → `429`
- `test_ask_creates_conversation` — first ask → new `conversation_id` in response
- `test_delete_document_not_owner` → `403`

---

## 13. Deployment Notes

### Local

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
# Then open: http://localhost:8000/login.html
```

### Docker (update Dockerfile CMD — no change needed if already using `backend.main:app`)

```bash
docker build -t sceneforge .
docker run -p 8000:8000 --env-file .env sceneforge
# Open: http://localhost:8000/login.html
```

### Railway (free tier)

1. Push to GitHub
2. New Railway project → Deploy from GitHub repo
3. Set env vars: `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`
4. Railway auto-detects Dockerfile and deploys

---

## 14. Glossary Additions

| Term | Definition |
|------|------------|
| **RLS** | Row Level Security — Postgres feature that filters rows based on the calling user's identity, enforced by Supabase |
| **JWT** | JSON Web Token — signed token returned by Supabase Auth on login; sent as `Authorization: Bearer <token>` header |
| **profiles table** | Custom table mirroring `auth.users`; used for rate-limit counters since `auth.users` cannot be queried from client |
| **conversation_id** | UUID grouping a series of messages within one chat session in one project |
| **rate limit** | 100 questions per user per calendar day; tracked in `profiles.questions_today` and reset when `last_question_date` changes |
| **cascade delete** | When a project is deleted, all child rows in `documents`, `document_chunks`, `conversations`, `messages` are automatically deleted via FK `ON DELETE CASCADE` |

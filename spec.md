# SceneForge — Kiro Spec

## 1. Project Overview

SceneForge is a RAG (Retrieval-Augmented Generation) chatbot for filmmakers. Users upload PDF research documents and ask natural-language questions that are answered **only** from those documents, with exact source citations.

**Problem it solves:** Filmmakers waste hours searching through 40+ PDFs. Generic AI hallucinates facts. SceneForge gives grounded answers with exact sources.

**Stack:**
- Backend: Python 3.11, FastAPI
- AI: Google Gemini 2.5 Flash (free tier) — embeddings + generation
- Database: Supabase (PostgreSQL + pgvector)
- PDF parsing: PyMuPDF (fitz)
- Memory: Mem0 (local file storage)
- Frontend: Vanilla HTML/JS (single file, no framework)
- Deployment: Docker

---

## 2. Functional Requirements

| ID  | Requirement | Priority |
|-----|-------------|----------|
| F1  | User can upload PDF files (max 50 MB per file, 30 files per project) | P0 |
| F2  | System extracts text from uploaded PDFs page-by-page | P0 |
| F3  | System chunks text into overlapping pieces (500 words, 50-word overlap) | P0 |
| F4  | System generates 768-dim embeddings for each chunk via Gemini `embedding-001` | P0 |
| F5  | Chunks + embeddings stored in Supabase `document_chunks` table, scoped to `project_id` | P0 |
| F6  | User can type questions in a chat interface | P0 |
| F7  | System retrieves top-5 most relevant chunks per question via cosine similarity | P0 |
| F8  | System answers using ONLY retrieved chunks + Gemini; never adds outside knowledge | P0 |
| F9  | Answers include source filename and page number for every cited fact | P0 |
| F10 | System persists project facts across sessions using Mem0 local memory | P1 |
| F11 | Different filmmaker projects are fully isolated (no cross-project data leakage) | P1 |
| F12 | User sees upload progress indicator during PDF processing | P2 |
| F13 | User sees animated loading spinner while waiting for an answer | P2 |

---

## 3. Non-Functional Requirements

| ID  | Requirement | Target |
|-----|-------------|--------|
| N1  | First-token response time for a question | < 3 seconds |
| N2  | PDF upload + processing time | < 10 seconds per 100 pages |
| N3  | Concurrent users (free-tier safe) | 10 |
| N4  | Gemini API daily request budget | < 1,500 requests/day |
| N5  | Supabase vector storage per project | ≤ 500 MB total (free tier) |

---

## 4. Architecture

### 4.1 Component Diagram

```
Browser (index.html)
      │  HTTP POST/GET
      ▼
FastAPI (main.py)
  ├── /upload    → rag.py → Supabase
  ├── /ask       → memory.py + rag.py → Gemini + Supabase
  ├── /project/{id} DELETE
  └── /health

External services:
  • Supabase (pgvector) — chunk storage + similarity search
  • Gemini Flash       — embeddings + generation
  • Mem0 (local)       — cross-session project memory
```

### 4.2 PDF Upload Flow

```
PDF File
  → PyMuPDF         extract text per page
  → chunk_text()    split into 500-word / 50-word overlap chunks
  → get_embedding() Gemini embedding-001 (768 dims)
  → Supabase INSERT document_chunks (project_id, filename, page_num, chunk_text, embedding)
```

### 4.3 Question-Answer Flow

```
User question
  → get_embedding()       embed question (task_type="retrieval_query")
  → Supabase RPC          match_chunks() cosine similarity, top 5, filtered by project_id
  → get_project_memory()  Mem0 facts for this project
  → build_prompt()        system + memory + [SOURCE N] blocks + question
  → Gemini Flash          generate answer with inline citations
  → save_conversation_memory()  persist Q&A to Mem0
  → return {reply, sources}
```

---

## 5. Database Schema (Supabase / PostgreSQL)

### Enable extension (run once)

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Table: `document_chunks`

```sql
CREATE TABLE document_chunks (
    id          BIGSERIAL PRIMARY KEY,
    project_id  TEXT      NOT NULL,
    filename    TEXT      NOT NULL,
    page_num    INTEGER,
    chunk_text  TEXT      NOT NULL,
    embedding   VECTOR(768),
    created_at  TIMESTAMP DEFAULT NOW()
);

-- ANN index for fast cosine similarity search
CREATE INDEX ON document_chunks
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Filter index for project isolation
CREATE INDEX ON document_chunks (project_id);
```

### Table: `projects` (optional metadata)

```sql
CREATE TABLE projects (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW(),
    document_count  INTEGER DEFAULT 0,
    total_pages     INTEGER DEFAULT 0
);
```

### RPC: `match_chunks`

```sql
CREATE OR REPLACE FUNCTION match_chunks(
    query_embedding VECTOR(768),
    project_id      TEXT,
    match_count     INTEGER DEFAULT 5
)
RETURNS TABLE(
    chunk_text  TEXT,
    filename    TEXT,
    page_num    INTEGER,
    similarity  FLOAT
)
LANGUAGE SQL STABLE AS $$
    SELECT
        chunk_text,
        filename,
        page_num,
        1 - (embedding <=> query_embedding) AS similarity
    FROM document_chunks
    WHERE document_chunks.project_id = match_chunks.project_id
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;
```

> **Run all three SQL blocks in the Supabase SQL Editor before starting the server.**

---

## 6. File Structure

```
sceneforge/
├── backend/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, all endpoints
│   ├── rag.py           # PDF extraction, chunking, embedding, search, answer
│   ├── memory.py        # Mem0 save/retrieve/clear helpers
│   ├── models.py        # Pydantic request/response models
│   ├── config.py        # Env-var loading + constants
│   └── utils.py         # (reserved for future helpers)
├── frontend/
│   └── index.html       # Complete single-file UI
├── uploads/             # Temp PDF storage (git-ignored)
├── tests/
│   ├── test_rag.py
│   └── test_api.py
├── .env                 # API keys (git-ignored)
├── .gitignore
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 7. Environment Variables (`.env`)

```env
# Google AI Studio — https://aistudio.google.com/apikey
GEMINI_API_KEY=your_key_here

# Supabase project — https://supabase.com (free tier)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
```

Mem0 defaults to local file storage (`./mem0/` directory). No additional key required for development.

---

## 8. Configuration Constants (`backend/config.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `CHUNK_SIZE` | 500 | Words per chunk |
| `CHUNK_OVERLAP` | 50 | Overlapping words between consecutive chunks |
| `TOP_K_CHUNKS` | 5 | Chunks retrieved per question |
| `GEMINI_MODEL` | `"gemini-2.0-flash-exp"` | Generation model |
| `EMBEDDING_MODEL` | `"models/embedding-001"` | Embedding model |
| `EMBEDDING_DIMENSION` | 768 | Must match `VECTOR(768)` in schema |
| `MAX_FILE_SIZE_MB` | 50 | Per-file upload limit |
| `MAX_FILES_PER_PROJECT` | 30 | Total files per project |

---

## 9. API Endpoints

### `GET /`
Returns the `frontend/index.html` content. Serves the full UI.

---

### `POST /upload`
Upload and process a PDF.

**Form fields:**
- `file` — PDF binary (multipart)
- `project_id` — string identifier for the project

**Validation:**
- File extension must be `.pdf`
- File size must be ≤ `MAX_FILE_SIZE_MB` (50 MB)

**Processing steps:**
1. Save file temporarily to `uploads/{project_id}_{filename}`
2. Call `process_and_store_pdf(path, filename, project_id)`
3. Delete temp file (even on error)
4. Return `UploadResponse`

**Success response (`200`):**
```json
{
  "success": true,
  "filename": "script_research.pdf",
  "chunks_created": 142,
  "message": "Successfully processed script_research.pdf. Created 142 searchable chunks."
}
```

**Error responses:**
- `400` — not a PDF / file too large
- `500` — processing failure (Gemini / Supabase error)

---

### `POST /ask`
Ask a question about uploaded documents.

**Request body:**
```json
{
  "message": "What did sources say about police procedures in 1983?",
  "project_id": "MyBombayFilm",
  "history": []
}
```

**Processing steps:**
1. Validate message is non-empty
2. `get_project_memory(project_id)` — fetch Mem0 facts
3. `answer_with_sources(message, project_id, memory)` — embed + retrieve + generate
4. `save_conversation_memory([user_msg, assistant_msg], project_id)` — persist to Mem0
5. Return `ChatResponse`

**Success response (`200`):**
```json
{
  "reply": "According to [SOURCE 1: research.pdf, page 12], officers in 1983...",
  "sources": [
    {
      "filename": "research.pdf",
      "page": 12,
      "text_preview": "First 200 chars of chunk..."
    }
  ]
}
```

**Error responses:**
- `400` — empty message
- `500` — Gemini / Supabase failure

---

### `DELETE /project/{project_id}`
Delete all document chunks and Mem0 memory for a project.

**Response (`200`):**
```json
{ "message": "Deleted 847 document chunks and cleared memory" }
```

---

### `GET /health`
Liveness check.

**Response (`200`):**
```json
{ "status": "healthy", "gemini_configured": true }
```

---

## 10. Module Specifications

### `backend/config.py`
- Load `.env` via `python-dotenv`
- Export all constants as module-level variables
- No class, no lazy loading — import and done

### `backend/models.py`
Pydantic v2 models:

| Model | Fields |
|-------|--------|
| `ChatRequest` | `message: str`, `project_id: str`, `history: List[dict] = []` |
| `ChatResponse` | `reply: str`, `sources: List[dict]` |
| `UploadResponse` | `success: bool`, `filename: str`, `chunks_created: int`, `message: str` |
| `ProjectMemoryResponse` | `memories: List[str]` |

### `backend/rag.py`

#### `extract_text_from_pdf(pdf_path: str) -> List[Dict]`
- Open PDF with `fitz.open()`
- Iterate pages (1-indexed)
- Return `[{"text": str, "page": int}]`, skipping blank pages

#### `chunk_text(text: str, chunk_size=500, overlap=50) -> List[str]`
- Split on whitespace into words
- Return `[text]` as-is if fewer than 50 words
- Sliding window: `start=0`, `end=start+chunk_size`, next `start=end-overlap`
- Stop when `start >= len(words)`

#### `get_embedding(text: str) -> List[float]`
- Call `genai.embed_content(model=EMBEDDING_MODEL, content=text, task_type="retrieval_document")`
- Return `response['embedding']`
- **Note:** Use `task_type="retrieval_query"` for question embeddings in `search_documents`

#### `process_and_store_pdf(pdf_path, filename, project_id) -> int`
- Loop pages → chunks
- Skip chunks shorter than 50 characters
- For each valid chunk: get embedding → INSERT to `document_chunks`
- Return total chunks stored

#### `search_documents(question, project_id, top_k=5) -> List[Dict]`
- Embed question with `task_type="retrieval_query"`
- Call Supabase RPC `match_chunks`
- Return `result.data`

#### `build_prompt(question, chunks, project_memory="") -> str`
- Inject `project_memory` block if non-empty
- Format each chunk as `[SOURCE N: filename, page N]\n{chunk_text}`
- Include strict system instructions: answer only from sources, cite every claim, say "I cannot find this information" if not present

#### `answer_with_sources(question, project_id, project_memory="") -> Tuple[str, List[Dict]]`
- Calls `search_documents` → if no results return early with empty sources list
- Calls `build_prompt` → calls `genai.GenerativeModel(GEMINI_MODEL).generate_content(prompt)`
- Returns `(answer_text, sources_list)` where each source has `filename`, `page`, `text_preview` (first 200 chars + "...")

#### `delete_project_documents(project_id) -> int`
- `supabase.table('document_chunks').delete().eq('project_id', project_id).execute()`
- Return `len(result.data)`

### `backend/memory.py`

#### `save_conversation_memory(messages: List[Dict], user_id: str)`
- Call `memory.add(messages, user_id=user_id)`
- Silently catch and log exceptions — never raise

#### `get_project_memory(user_id: str) -> str`
- Call `memory.get_all(user_id=user_id)`
- Return `""` on empty result or exception
- Format up to 10 memories as bullet list prefixed with a context header

#### `clear_project_memory(user_id: str)`
- Call `memory.delete_all(user_id=user_id)`
- Silently catch and log exceptions

### `backend/main.py`
- Initialize FastAPI with title/description
- Add `CORSMiddleware` with `allow_origins=["*"]` (dev only)
- Create `uploads/` directory on startup with `Path.mkdir(exist_ok=True)`
- Import all models, rag, memory modules using **relative imports** (not `backend.rag`) because the app runs from inside `backend/` or via Docker `WORKDIR /app`
- The Dockerfile's `CMD` is `uvicorn backend.main:app` so imports inside `main.py` should be `from models import ...` (relative, no package prefix)

---

## 11. Frontend (`frontend/index.html`)

Single self-contained HTML file. No build step, no framework.

### Layout
- Dark gradient background (`#1a1a2e → #16213e`)
- Two-column grid: 300px sidebar + flex chat area
- Sidebar: upload dropzone + uploaded file list
- Chat area: scrollable message list + text input + Send button

### State (in-memory + localStorage)
| Key | Storage | Purpose |
|-----|---------|---------|
| `sceneforge_project_id` | localStorage | Persists project name across reloads |
| `sceneforge_files_{project_id}` | localStorage | Persists uploaded file list for display |
| `messageHistory` | JS variable | Rolling array of `{role, content}` sent to `/ask` |
| `uploadedFiles` | JS variable (synced to localStorage) | File names + chunk counts for sidebar |

### Key Behaviors
1. **On load:** Read `project_id` from localStorage; if absent, `prompt()` user for project name
2. **File input change:** For each file, POST to `/upload` with `FormData`; animate progress bar; on success append to file list and chat
3. **Send message:** POST to `/ask`; show typing indicator; on response render assistant bubble with source tags
4. **Enter key:** Triggers `sendMessage()`
5. **Source tags:** Hoverable `<span>` elements showing `filename (p.N)` with tooltip of chunk preview

### Chat Message Rendering
- User messages: right-aligned green bubble
- Assistant messages: left-aligned semi-transparent bubble
- Sources rendered as small `source-tag` spans below the bubble
- `fadeIn` CSS animation on every new message

---

## 12. Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY .env .
RUN mkdir -p uploads
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Import note for Docker:** Because `WORKDIR` is `/app` and the command is `uvicorn backend.main:app`, Python's module resolution makes `backend` a package. Imports inside `backend/main.py` must be:
```python
from backend.models import ...
from backend.rag import ...
from backend.memory import ...
import backend.config as config
```
Ensure `backend/__init__.py` exists (can be empty).

---

## 13. `requirements.txt`

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
google-generativeai==0.7.0
pymupdf==1.24.0
supabase==2.5.0
python-dotenv==1.0.0
mem0ai==0.1.0
pydantic==2.9.0
python-multipart==0.0.12
```

---

## 14. `.gitignore`

```
venv/
__pycache__/
*.pyc
.env
uploads/
.DS_Store
*.log
.pytest_cache/
.vscode/
*.db
mem0/
```

---

## 15. Setup & Run

### Local Development

```bash
# 1. Create project + virtual environment
mkdir sceneforge && cd sceneforge
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env            # Fill in GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY

# 4. Run database migrations
#    Open Supabase SQL Editor and execute:
#    - CREATE EXTENSION IF NOT EXISTS vector;
#    - CREATE TABLE document_chunks ...
#    - CREATE INDEX (ivfflat) ...
#    - CREATE INDEX (project_id) ...
#    - CREATE OR REPLACE FUNCTION match_chunks ...

# 5. Start server
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 6. Open browser
open http://localhost:8000
```

### Docker

```bash
docker build -t sceneforge .
docker run -p 8000:8000 --env-file .env sceneforge
```

---

## 16. Known Constraints & Gotchas

| # | Issue | Mitigation |
|---|-------|------------|
| 1 | Gemini `embedding-001` uses `task_type` field — use `"retrieval_document"` for chunks, `"retrieval_query"` for questions | Hardcoded in `get_embedding()` and `search_documents()` |
| 2 | Supabase `ivfflat` index requires at least ~100 rows before it becomes effective | Document in README; acceptable for MVP |
| 3 | `mem0ai` local storage writes to `./mem0/` relative to CWD — add to `.gitignore` | Already in `.gitignore` |
| 4 | Docker import paths differ from local dev (`backend.rag` vs `rag`) | Use `backend.X` style imports in all files; ensure `__init__.py` exists |
| 5 | PyMuPDF package name is `pymupdf` in pip but imported as `fitz` | Correct in `requirements.txt` and `import fitz` in `rag.py` |
| 6 | Supabase `delete()` returns empty `data` list on some client versions | Use `len(result.data)` safely (returns 0, not error) |
| 7 | `localStorage` in the browser persists project ID and file list — clearing browser storage resets UI but not Supabase data | Use the `DELETE /project/{id}` endpoint to fully purge |
| 8 | `MAX_FILES_PER_PROJECT` limit is not enforced server-side in the current spec | Add count check to `/upload` handler in a future iteration |

---

## 17. Test Plan

### `tests/test_rag.py`
- `test_chunk_text_basic` — verify chunk count and overlap for a 1000-word input
- `test_chunk_text_short` — input < 50 words returns single chunk
- `test_chunk_text_empty` — empty string returns `[]`
- `test_extract_text_returns_pages` — mock fitz, verify list structure
- `test_build_prompt_contains_sources` — verify SOURCE blocks appear in output
- `test_build_prompt_with_memory` — verify memory block injected when non-empty
- `test_build_prompt_no_hallucination_instruction` — verify "ONLY" instruction present

### `tests/test_api.py`
- `test_health_endpoint` — returns 200 with `status: healthy`
- `test_upload_non_pdf_rejected` — `.txt` file returns 400
- `test_ask_empty_message_rejected` — empty string returns 400
- `test_ask_returns_reply_and_sources` — mock `answer_with_sources`, verify response shape
- `test_delete_project` — mock `delete_project_documents` + `clear_project_memory`, verify 200

---

## 18. Glossary

| Term | Definition |
|------|------------|
| **Chunk** | A 500-word (approx.) slice of PDF text, with 50-word overlap with adjacent chunks |
| **Embedding** | A 768-dimensional float vector representing semantic meaning of a text chunk |
| **project_id** | A user-defined string (e.g. `"MyBombayFilm"`) that namespaces all data for one filmmaker's project |
| **RAG** | Retrieval-Augmented Generation — the pattern of retrieving relevant context before generating an answer |
| **Mem0** | A Python library that extracts and stores factual memories from conversations for long-term context |
| **pgvector** | A PostgreSQL extension that adds vector column types and ANN (approximate nearest neighbour) search |
| **ivfflat** | An ANN index type in pgvector using inverted file structure — fast cosine similarity at scale |

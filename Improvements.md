Let me read all the key files at once to do a thorough analysis.

Viewed state.py:1-800
Viewed rag.py:1-411
Viewed memory.py:1-120

Now let me read the backend main file and the remaining state.py section to complete the picture.

Listed directory backend
Viewed state.py:800-898
Viewed main.py:1-682
Viewed config.py:1-68

I've read every critical file. Here's the complete, honest breakdown of everything making your app slow:

---

## 🐌 Every Single Bottleneck — Ranked by Impact

### 🔴 CRITICAL (Biggest Killers)

---

**1. HyDE (Hypothetical Document Expansion) — adds 1-2 extra Gemini API calls per question**
> `rag.py` line 243 — `generate_hyde_response(question)` runs a full Gemini `generate_content` call BEFORE the actual vector search. So every question = 2 Gemini calls minimum before you even get an answer. This alone is the #1 cause of slow Q&A.

---

**2. `/ask` endpoint calls `get_project_memory` (Mem0 + Qdrant) on every single question**
> `main.py` line 511 — `memory_fut = asyncio.to_thread(get_project_memory, ...)`. Mem0 does an **embedding call + local Qdrant vector search** to fetch memories every time. Cold Qdrant reads from disk are slow.

---

**3. `load_project_details` calls `/projects` (full list) just to verify one project**
> `state.py` line 608 — Every time you open a project, it fetches **all your projects**, then loops to find the matching one. Should be a single `/projects/{id}` call. This is pure wasted round trip.

---

**4. Three separate API calls on project load (sequential auth check)**
> `on_load_project` → `check_auth()` → `/auth/me` (1st call), then `load_project_details()` → `/projects` (2nd call), then `load_documents`, `load_profile` → `/auth/me` again (3rd call). **`/auth/me` is called twice per page load.**

---

**5. `check_rate_limit` in `/ask` does synchronous Supabase reads inside a sync function called from async**
> `main.py` line 519 — `check_rate_limit` is a blocking sync call on the async event loop. It reads from Supabase synchronously. Then right after it, there's ANOTHER `profile_res` query (line 557) to get `questions_today`. **The rate limit is checked AND re-fetched = 2 DB reads.**

---

**6. Gemini `gemini-2.5-flash` thinking model — slow by default**
> `config.py` line 43 — `gemini-2.5-flash` has a thinking budget. Even with `thinking_budget=0` it may still spin up reasoning. For RAG answers, `gemini-1.5-flash` or `gemini-2.0-flash` would be 2–3× faster.

---

### 🟠 HIGH IMPACT

---

**7. `process_callback_hash` creates a brand new `httpx.AsyncClient` (new TCP connection) on every Google OAuth callback**
> `state.py` line 355 — `async with httpx.AsyncClient(...)` — this creates a fresh connection instead of using the shared `_get_http_client()` pool. Minor for login frequency but wastes time.

---

**8. Dashboard `/projects` endpoint fetches ALL documents table to count per project**
> `main.py` lines 232–238 — `db.table("documents").select("project_id").execute()` — **no filter**. This fetches every document row from every user to count docs per project. Grows worse as the DB grows.

---

**9. `start_document_polling` polls every 0.5 seconds in a tight background loop**
> `state.py` line 719 — `await asyncio.sleep(0.5)`. Each poll hits `/documents/{project_id}` which hits Supabase. Should be 2–3s interval and use exponential backoff once docs are processing.

---

**10. `auth/me` endpoint does a Supabase DB read AND potentially an INSERT on every hit**
> `main.py` lines 166–180 — Every `/auth/me` call reads from `profiles` table, and on first-time users does an INSERT. This endpoint is called on every page load AND on every project open.

---

**11. Vector search uses `candidate_limit = top_k * 2` for BOTH vector AND FTS search separately**
> `rag.py` line 237 — Fetches `10` chunks from vector + `10` from FTS, then RRF-merges to get 5. The double-fetching is intentional but means 2 Supabase RPC calls on every question.

---

### 🟡 MODERATE IMPACT

---

**12. `get_authenticated_client` creates a NEW Supabase client per request with the user token**
> `auth.py` (inferred) — If it's `create_client()` per-call, that's a new HTTP client instantiation per request. No connection reuse across requests.

---

**13. Mem0 uses local Qdrant file storage (`./mem0`) — disk I/O on every memory read**
> `memory.py` line 50 — `"path": "./mem0"` means Qdrant reads from disk every time. If the memory store grows, this gets slower.

---

**14. Login form `handle_auth` posts credentials as URL query params instead of JSON body**
> `state.py` line 255 — `params={"email": ..., "password": ...}` — query params travel in the URL. Functionally fine but shows no optimization mindset, and params get logged by middleware.

---

**15. Chat history load fetches last conversation then fetches all its messages (2 sequential queries)**
> `main.py` lines 606–618 — First queries `conversations` table, then queries `messages` table. Could be a single JOIN query.

---

### 🟢 MINOR BUT WORTH FIXING

---

**16. `scroll_to_bottom` is called with `yield` + async overhead for a JS one-liner**
> Every message send triggers two separate `yield` + `scroll_to_bottom` calls. Minor overhead but adds up.

---

**17. `handle_upload` reads the full file contents in state, then re-sends to `/upload` which reads it again**
> `state.py` line 661 + `main.py` line 440 — Double memory allocation. The file is in RAM twice.

---

**18. `filtered_projects` `@rx.var` runs on every state change (including unrelated ones)**
> `state.py` line 486 — A computed var that filters the entire project list re-runs on any state mutation, including typing into unrelated fields.

---

## Summary Priority Order

| Priority | Issue | Time Saved |
|---|---|---|
| 🔴 #1 | Disable/remove HyDE (extra Gemini call before every answer) | **~1-3s per question** |
| 🔴 #2 | Remove Mem0 memory fetch from the hot path of `/ask` | **~0.5-2s per question** |
| 🔴 #3 | Fix project load — use a direct `/projects/{id}` endpoint | **~300-600ms per open** |
| 🔴 #4 | Eliminate the duplicate `/auth/me` call on project load | **~200-400ms per open** |
| 🔴 #5 | Fix duplicate rate-limit DB reads in `/ask` | **~200ms per question** |
| 🟠 #6 | Switch to `gemini-2.0-flash` or `gemini-1.5-flash` for generation | **~1-2s per question** |
| 🟠 #7 | Fix `/projects` fetching all documents for count — add filter or SQL count | **~200ms on dashboard** |
| 🟠 #8 | Reduce polling interval from 0.5s → 3s | **reduces server load** |

Want me to go ahead and fix all of these now?

**Potential Sources of Slowness in ScriptForge**  

Below is a high‑level checklist of every area that can introduce latency from the moment a user logs in → project list loads → PDF is fetched/parsed → question‑answering request is processed. Review each item in your codebase, infrastructure, and third‑party services to pinpoint the biggest contributors.

---

### 1. Client‑Side (Browser)  
| Symptom | Likely Cause |
| ------- | ------------ |
| Slow page render, janky UI | • Large, un‑compressed JS/CSS bundles (no code‑splitting) <br>• Blocking synchronous scripts (e.g., heavy `fetch` in `onload`) <br>• Lack of lazy‑loading for images/PDF thumbnails |
| Delayed interactions after login | • Excessive DOM updates or re‑flows <br>• Missing `requestAnimationFrame` for animations <br>• No use of **Cache‑Control** / Service Worker for static assets |

**Quick audit steps** – open `pages/*.py` (e.g., `callback.py`, `project.py`) and check the templating for inline scripts or large `<style>` blocks; inspect the network panel for resource sizes.

---

### 2. Network / API Layer  
| Symptom | Likely Cause |
| ------- | ------------ |
| High round‑trip time between login & dashboard | • Multiple sequential API calls (e.g., separate request for user profile, then projects) <br>• No HTTP keep‑alive / connection pooling on the client |
| PDF fetch appears slow | • PDF stored on remote storage without CDN <br>• No `Range` requests, forcing whole file download each time |
| Question‑answering latency | • Calls to external LLM / AI service without async handling <br>• Re‑creating auth tokens or re‑establishing gRPC streams per request |

**Tools** – use Chrome DevTools **Network** tab; look for `time` breakdown (DNS, Connect, Wait, Receive).  

---

### 3. Backend (Python / FastAPI / Flask)  
| Symptom | Likely Cause |
| ------- | ------------ |
| Login takes > 1 s | • Synchronous password hashing (`bcrypt`/`argon2`) without thread pool <br>• Blocking DB query for user lookup (no async/await) |
| Project list loads slowly | • N+1 queries when loading related data (e.g., tasks, members) <br>• Unindexed columns in Supabase (PostgreSQL) for filters/sorts |
| PDF processing bottleneck | • PDF parsing done on request thread (e.g., `pdfminer`, `PyMuPDF`) – heavy CPU <br>• No streaming; whole file read into memory |
| QA request lag | • Model inference executed synchronously on a single worker <br>• Re‑loading model weights on every request instead of caching in memory |
| General | • Global interpreter lock (GIL) contention when using CPU‑bound libs <br>• Lack of connection pooling for Supabase client <br>• Debug logging at `DEBUG` level writing to disk synchronously |

**Files to inspect** – `backend/auth.py` (login flow), `pages/project.py` (project loading), `pages/callback.py` (post‑login redirect), `rxconfig.py` (global config for DB/AI clients).

---

### 4. Database (Supabase / PostgreSQL)  
| Symptom | Likely Cause |
| ------- | ------------ |
| Slow `SELECT` for projects | • Missing indexes on `user_id`, `created_at`, `status` columns <br>• Large tables scanned without pagination (`LIMIT/OFFSET`) |
| PDF metadata queries | • Storing PDF blobs directly in the DB → large row reads <br>• No `EXPLAIN`‑based query tuning |
| Frequent auth checks | • Re‑querying user‑session table on every endpoint instead of JWT verification |

**Quick checks** – run `EXPLAIN ANALYZE` on the most common queries; verify indexes exist via `supabase_schema.sql`.

---

### 5. PDF Handling & Storage  
| Symptom | Likely Cause |
| ------- | ------------ |
| PDF preview stalls | • PDFs stored on a raw bucket without CDN edge caching <br>• On‑the‑fly conversion (e.g., to images) performed for every request |
| Server CPU spikes | • Re‑parsing same PDF for each question; no caching of extracted text <br>• Using heavyweight libraries (e.g., `pdfplumber`) in single‑threaded mode |

**Mitigations** – cache extracted text in Redis/memory; pre‑generate image thumbnails; serve PDFs via a CDN with `Cache‑Control:max-age`.

---

### 6. AI / LLM Inference  
| Symptom | Likely Cause |
| ------- | ------------ |
| Answer generation > 2 s | • Model weight loading per request (cold start) <br>• No request batching; each question hits the remote endpoint separately <br>• Synchronous HTTP call to Gemini API without timeout handling |
| High latency spikes | • Network egress throttling from your cloud region to the AI endpoint <br>• Rate‑limit back‑off causing retries |

**Tip** – keep the model client instantiated globally (singleton) and reuse the same session; enable streaming or async calls if supported.

---

### 7. Infrastructure / Hosting  
| Symptom | Likely Cause |
| ------- | ------------ |
| Overall app feels “heavy” | • Under‑provisioned container (CPU/RAM) – CPU throttling on PDF parsing & model inference <br>• Single‑instance deployment without load‑balancing <br>• No HTTP/2 or gzip compression enabled |
| Cold starts after idle | • Serverless functions with long cold‑start times (e.g., Vercel edge functions) <br>• Database connection pool closed after inactivity |

**Check** – look at your deployment platform (Firebase, Vercel, Docker) and inspect resource limits; enable gzip/brotli, HTTP/2, and keep‑alive.

---

### 8. Authentication / Session Management  
| Symptom | Likely Cause |
| ------- | ------------ |
| Login → redirect delay | • Re‑validating JWT on every request against auth server instead of local verification <br>• Session store (e.g., Redis) on a remote region causing network latency |
| Re‑auth on PDF fetch | • Token refresh triggered for each static asset request |

**Review** – `backend/auth.py` for token handling; confirm you’re using short‑lived JWTs verified locally.

---

### 9. Miscellaneous / Code Quality  
| Symptom | Likely Cause |
| ------- | ------------ |
| Unexpected spikes | • Synchronous `time.sleep` or `await asyncio.sleep` used for debugging left in production <br>• Heavy third‑party SDK initializations inside request handlers (e.g., `firebase-admin` client) |
| Memory pressure | • Leaking file handles when reading PDFs, leading to GC pauses <br>• Large in‑memory data structures (e.g., full project list) sent to the client without pagination |

**Action** – run a profiler (e.g., `cProfile`, `pyinstrument`) on a typical request flow; look for “hot” functions.

---

## How to Prioritise Investigation  

1. **Instrument & Measure** – add timing logs (start/end) around:  
   * login DB query (`auth.py`)  
   * project list retrieval (`project.py`)  
   * PDF fetch & parse (`callback.py` or dedicated PDF utils)  
   * AI inference call (Gemini/LLM client)  

2. **Collect real‑world metrics** – use Chrome DevTools **Performance** trace for a full user journey; note the longest “Main” thread tasks and network wait times.

3. **Apply the “biggest‑impact first” rule** – typically:  
   * Database query inefficiencies (add indexes, paginate)  
   * CPU‑bound PDF parsing (cache results, move to background worker)  
   * AI inference latency (reuse model client, enable async)  

4. **Iterate** – after each optimisation, re‑run the trace to verify the improvement before moving to the next item.

---

**Next steps (if you’d like us to dive deeper)**  
- Run an explicit performance profile on the login and project endpoints.  
- Show the most common SQL queries from `supabase_schema.sql`.  
- Inspect the PDF handling code for blocking I/O.  

Let us know which area you’d like to explore first, or share any logs/trace data you have, and we can propose concrete code changes.

I will list the directory contents of your workspace to locate the source code files and understand the project structure. This will help me analyze the exact code causing the slow performance.

Listed directory ScriptForge

I will list the contents of the `sceneforge` directory to identify the Python modules responsible for routing, state management, and page views.

Listed directory sceneforge

I will list the files inside `sceneforge/pages` to see the structure of the front-end pages.

Listed directory pages

I will read the `requirements.txt` file to check the dependencies and libraries used in this project. This helps me understand what tools (like DB connectors, PDF parsers, AI SDKs) are in use and how they might contribute to latency.

Viewed requirements.txt:1-14

I will read the `sceneforge/state.py` file to inspect the database operations, API calls, and logic for authentication, projects loading, and question-answering. This is the central state file where performance bottlenecks are most likely located.

Viewed state.py:1-800

I will view the rest of the `sceneforge/state.py` file to see the document preview/loading logic.

Viewed state.py:801-898

I will list the contents of the `backend` directory to find the FastAPI server code and identify the logic implementing database access, authentication, PDF parsing, and AI questioning.

Listed directory backend

I will read the `backend/main.py` file to understand the core logic of the FastAPI backend, how it communicates with Supabase, processes documents, and interfaces with AI. This is where many backend performance issues (like database connection overhead, loops, or synchronous calls) are likely located.

Viewed main.py:1-682

I will read `backend/auth.py` to examine the authentication flow, how the token is validated, user profile lookups, and supabase client initialization, looking for synchronous network calls, slow connections, or repeated operations.

Viewed auth.py:1-265

I will read `backend/rag.py` to examine the document parsing, vector database insertion, and retrieval/LLM query processing, identifying where the latency during PDF upload and answering questions originates.

Viewed rag.py:1-411

I will read `backend/memory.py` to see how the project memory is fetched and saved using `mem0` or other integrations. Large/slow network calls or memory searches could add to latency.

Viewed memory.py:1-120

I will read `backend/config.py` to check the default settings, limits, chunk sizes, and models configured for Gemini and embeddings. This will help understand the limits and dimensions that could impact processing time.

Viewed config.py:1-68

I will read `sceneforge/pages/login.py` to check the front-end login view structure and look for any components, triggers, or API integrations during login.

Viewed login.py:1-150

I will view `sceneforge/sceneforge.py` to see the route configurations, page definitions, and their `on_load` event handlers. This will show us how page loading is orchestrated.

Viewed sceneforge.py:1-69

I will view the first 200 lines of `sceneforge/pages/project.py` to examine the page structure and find how the initialization event/handler is hooked up.

Viewed project.py:1-200

I will view the end of `sceneforge/pages/project.py` to see the entry point for the project page and how `on_load` or initialization events are registered.

Viewed project.py:900-1050

I will read the `supabase_schema.sql` file to understand the database schema, indexes, foreign key relationships, and RLS (Row Level Security) policies. This will clarify how queries can be optimized (e.g. by using database-level joins or aggregation).

Viewed supabase_schema.sql:1-196

Here is a comprehensive breakdown of every bottleneck and latency source causing the application to feel slow, categorized by flow.

---

### 1. Authentication & Login Flow

*   **Synchronous Supabase Network Requests:** 
    During `login` and `signup` in [backend/auth.py](file:///Users/shameekyogi/My%20Apps/ScriptForge/backend/auth.py#L136-L149), the application makes blocking synchronous calls to the Supabase Auth API (`auth.sign_in_with_password` and `auth.sign_up`). Under network latency, this blocks the entire FastAPI worker thread.
*   **Sequential Profile Creation:** 
    Upon signup, a database write to the `profiles` table is executed synchronously, adding database network round-trip time directly into the critical path of the authentication response.
*   **JWT Verification Cache Misses:** 
    The `/auth/me` endpoint in [backend/main.py](file:///Users/shameekyogi/My%20Apps/ScriptForge/backend/main.py#L161-L190) is called on almost every page load. If the user cache has expired or misses, the backend makes a synchronous request to Supabase (`auth.get_user(token)`) to verify the JWT, blocking the thread.
*   **FastAPI Sync Thread Pool Overhead:** 
    All authentication endpoints (`/auth/login`, `/auth/signup`, and `/auth/me`) are defined as synchronous `def` functions. FastAPI handles synchronous functions by offloading them to a thread pool (`anyio.to_thread.run_sync`), which introduces context-switching overhead and limits concurrency.

---

### 2. Projects Dashboard Loading

*   **Table-Wide Fetch for Counting Documents (N+1 Query):** 
    In [backend/main.py](file:///Users/shameekyogi/My%20Apps/ScriptForge/backend/main.py#L229-L238), to compute the document counts for a user's projects, the backend executes:
    ```python
    docs_res = db.table("documents").select("project_id").execute()
    ```
    This fetches **every document project ID in the entire database** and counts them sequentially in a Python loop. As the database grows, this query becomes extremely slow. 
*   **Lack of Joined Queries:** 
    Instead of performing a single PostgreSQL join or group-by query, the backend executes multiple separate, synchronous database requests to get projects and count their documents sequentially.

---

### 3. Entering the Project Page (Inside Project Loading)

*   **Chatty API Roundtrips:** 
    When the project workspace page is opened, `on_load_project` in [sceneforge/state.py](file:///Users/shameekyogi/My%20Apps/ScriptForge/sceneforge/state.py#L585-L603) triggers 5 separate HTTP calls to the backend:
    1. `check_auth()` $\rightarrow$ `GET /auth/me`
    2. `load_project_details()` $\rightarrow$ `GET /projects` (to look up the project name)
    3. `load_documents()` $\rightarrow$ `GET /documents/{project_id}`
    4. `load_profile()` $\rightarrow$ `GET /auth/me`
    5. `load_chat_history()` $\rightarrow$ `GET /projects/{project_id}/messages`
    
    Even with in-process routing, this results in **9 separate database queries** on Supabase executed sequentially, causing a noticeable loading delay.
*   **Redundant Project Ownership Checks:** 
    Because Row-Level Security (RLS) is already enabled on Supabase, the manual queries checking project ownership in `/documents/{project_id}` and `/projects/{project_id}/messages` are redundant and add unnecessary database roundtrips.

---

### 4. PDF Preview & Processing

*   **Reconstructing Page Text from Chunks:** 
    To display a PDF page preview in the workspace, the endpoint `/documents/{project_id}/page-text` queries the `document_chunks` table for every individual chunk on that page and concatenates them in Python:
    ```python
    res = db.table("document_chunks").select("chunk_text, id").eq(...).execute()
    ```
    Querying vectors and text chunks from database rows over the network just to render a page of text is highly inefficient compared to serving cached text or a dedicated file store.
*   **Chatty Document Polling:** 
    When a document is uploaded, `start_document_polling` in [sceneforge/state.py](file:///Users/shameekyogi/My%20Apps/ScriptForge/sceneforge/state.py#L700-L720) polls the database for document statuses **every 0.5 seconds** using a recursive state loop, flooding the database with queries.

---

### 5. Answering Questions (Chat Flow)

This is the slowest flow in the system, performing multiple slow network APIs and LLM invocations sequentially:

1. **HyDE Query Expansion (LLM Call 1):** 
   The RAG pipeline calls `generate_hyde_response` in [backend/rag.py](file:///Users/shameekyogi/My%20Apps/ScriptForge/backend/rag.py#L200-L221) which sends a request to `gemini-2.5-flash` to write a hypothetical answer. **(Adds 1.5 to 3 seconds)**
2. **Embedding API Call:** 
   The code calls the Gemini Embedding API synchronously to embed the expanded HyDE query. **(Adds 0.5 to 1 second)**
3. **Sequential Vector & FTS Database Searches:** 
   The vector similarity search (Supabase RPC `match_chunks`) and the Full-Text Search (Supabase `.wfts()`) are run sequentially rather than concurrently. **(Adds 0.5 seconds)**
4. **Final Answer Generation (LLM Call 2):** 
   The prompt is compiled and sent to Gemini to generate the final response. **(Adds 2 to 4 seconds)**
5. **Post-Generation Rate Limit Check:** 
   The user's remaining daily question limit is queried from the `profiles` table after generating the answer instead of beforehand, blocking the response transmission. **(Adds 0.2 seconds)**
6. **Mem0 Initialisation & Local Search:** 
   Retrieving `mem0` memory in `get_project_memory` requires loading the local Qdrant database and performing a synchronous similarity search. On the first question, initializing the `Memory` object from config also adds a cold-start overhead of **1 to 2 seconds**.
7. **No Streaming Support:** 
   Because the `/ask` endpoint does not stream responses back token-by-token, the user must wait for all the steps above to complete (often **5 to 10 seconds total**) before seeing any response in the UI.
import asyncio
import logging
import os
import re
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    File,
    Form,
    Header,
    HTTPException,
    Request,
    UploadFile,
    Response,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from postgrest import CountMethod

# Ensure root workspace is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import backend.config as config
from backend.logging_config import setup_logging
from backend.auth import (
    signup,
    login,
    get_current_user,
    check_rate_limit,
    refresh_supabase_token,
    get_authenticated_client,
    get_service_client,
)
from backend.rag import answer_with_sources, process_and_store_pdf
from backend.memory import save_conversation_memory, clear_project_memory

# Initialize logging
setup_logging()
logger = logging.getLogger("backend.main")

# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="ScriptIQ API",
    description="RAG-powered film research assistant API backend",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS Middleware Setup
cors_env = os.getenv("CORS_ALLOWED_ORIGINS")
if cors_env and cors_env.strip() == "*":
    cors_origins = ["*"]
else:
    cors_origins = [
        origin.strip() for origin in (cors_env or "").split(",") if origin.strip()
    ] or [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://sceneforge-aqua-ocean.reflex.run",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

# 1. Gzip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 2. Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# 3. Request body size limit middleware (10MB)
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_REQUEST_SIZE:
                return Response("Request entity too large", status_code=413)
        except ValueError:
            pass
    return await call_next(request)

# Setup uploads temp directory
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------
_UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def validate_uuid(value: str, name: str = "id") -> str:
    if not value or not _UUID_RE.match(value):
        raise HTTPException(status_code=400, detail=f"Invalid {name} format.")
    return value


def validate_non_empty_text(value: str, name: str, max_len: int = 2000) -> str:
    text = (value or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail=f"{name} cannot be empty.")
    if len(text) > max_len:
        raise HTTPException(status_code=400, detail=f"{name} must be {max_len} characters or fewer.")
    return text


# ---------------------------------------------------------------------------
# API Models
# ---------------------------------------------------------------------------
class UserMeResponse(BaseModel):
    id: str
    email: str
    questions_today: int = 0


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_id: str


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str


class AuthRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=254)
    password: str = Field(..., min_length=8, max_length=128)


class ProjectCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    project_id: str = Field(..., min_length=36, max_length=36)
    conversation_id: Optional[str] = Field(None, max_length=36)


class ChatResponse(BaseModel):
    reply: str
    sources: List[dict]
    conversation_id: str
    remaining_questions: int


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------
def get_token(authorization: Optional[str] = Header(None)) -> str:
    """Extract and validate the authorization token from headers."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")
    return authorization.replace("Bearer ", "")


def get_user(token: str = Depends(get_token)) -> Any:
    """Resolve the current authenticated user or raise 401."""
    return get_current_user(token)


# ---------------------------------------------------------------------------
# Auth Endpoints
# ---------------------------------------------------------------------------
@app.post("/auth/signup", response_model=AuthResponse)
@limiter.limit("10/minute")
def auth_signup_endpoint(request: Request, req: AuthRequest):
    """Sign up a new user and return tokens."""
    try:
        res = signup(req.email, req.password)
        access_token = res.session.access_token if res.session else ""
        refresh_token = res.session.refresh_token if res.session else ""
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": str(res.user.id)
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Signup endpoint failure")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login", response_model=AuthResponse)
@limiter.limit("20/minute")
def auth_login_endpoint(request: Request, req: AuthRequest):
    """Authenticate existing user and return tokens."""
    try:
        res = login(req.email, req.password)
        return {
            "access_token": res.session.access_token,
            "refresh_token": res.session.refresh_token,
            "user_id": str(res.user.id)
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Login endpoint failure")
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/auth/refresh", response_model=RefreshResponse)
@limiter.limit("30/minute")
def auth_refresh_endpoint(request: Request, req: RefreshRequest):
    """Refresh the access token using a refresh token."""
    try:
        access_token, refresh_token = refresh_supabase_token(req.refresh_token)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Refresh token endpoint failure")
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/auth/me", response_model=UserMeResponse)
@limiter.limit("60/minute")
def auth_me_endpoint(request: Request, token: str = Depends(get_token), user: Any = Depends(get_user)):
    """Fetch user profile details and retrieve questions_today, initializing profile if needed."""
    try:
        db = get_authenticated_client(token)
        res = db.table("profiles").select("questions_today").eq("id", str(user.id)).execute()
        today_count = 0
        if res.data and isinstance(res.data, list) and res.data:
            row = res.data[0]
            if isinstance(row, dict):
                today_count = row.get("questions_today", 0) or 0
        return {"id": str(user.id), "email": user.email, "questions_today": today_count}
    except Exception as e:
        logger.exception("Failed to retrieve profile in auth/me")
        return {"id": str(user.id), "email": user.email, "questions_today": 0}


# ---------------------------------------------------------------------------
# Projects Endpoints
# ---------------------------------------------------------------------------
@app.post("/projects")
@limiter.limit("30/minute")
def create_project_endpoint(
    request: Request,
    req: ProjectCreateRequest,
    token: str = Depends(get_token),
    user: Any = Depends(get_user),
):
    """Create a new project namespace owned by the user."""
    name = req.name.strip()
    try:
        db = get_authenticated_client(token)
        res = db.table("projects").insert({
            "id": str(uuid.uuid4()),
            "name": name,
            "user_id": str(user.id),
        }).execute()
        res_data = res.data
        if not isinstance(res_data, list) or not res_data:
            raise HTTPException(status_code=500, detail="Failed to insert project.")
        return res_data[0]
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Create project failed")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/projects")
@limiter.limit("120/minute")
def list_projects_endpoint(request: Request, token: str = Depends(get_token), user: Any = Depends(get_user)):
    """List all projects belonging to the authenticated user."""
    try:
        db = get_authenticated_client(token)
        res = db.table("projects").select("*, documents(count)").eq("user_id", str(user.id)).execute()
        data_list = res.data
        projects_list = []

        if isinstance(data_list, list):
            for p in data_list:
                if isinstance(p, dict):
                    created = str(p.get("created_at", ""))
                    p_copy = dict(p)
                    p_copy["created_date"] = created.split("T")[0] if "T" in created else created

                    docs_list = p.get("documents", [])
                    doc_count = docs_list[0].get("count", 0) if isinstance(docs_list, list) and docs_list else 0
                    p_copy["document_count"] = doc_count
                    projects_list.append(p_copy)
        return projects_list
    except Exception as e:
        logger.exception("List projects failed")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/projects/{project_id}")
@limiter.limit("120/minute")
def get_project_endpoint(
    request: Request,
    project_id: str,
    token: str = Depends(get_token),
    user: Any = Depends(get_user),
):
    """Fetch a single project's details."""
    validate_uuid(project_id, "project_id")
    try:
        db = get_authenticated_client(token)
        res = (
            db.table("projects")
            .select("id, name, created_at, user_id, documents(*), conversations(id, messages(role, content, sources))")
            .eq("id", project_id)
            .eq("user_id", str(user.id))
            .order("created_at", desc=True, foreign_table="conversations")
            .limit(1, foreign_table="conversations")
            .order("created_at", desc=False, foreign_table="conversations.messages")
            .limit(50, foreign_table="conversations.messages")
            .execute()
        )
        if not res.data:
            raise HTTPException(status_code=404, detail="Project not found or access denied")
        return res.data[0]
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Get project failed")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.delete("/projects/{project_id}")
@limiter.limit("30/minute")
def delete_project_endpoint(
    request: Request,
    project_id: str,
    token: str = Depends(get_token),
    user: Any = Depends(get_user),
):
    """Delete a project and clear all related documents and memories."""
    validate_uuid(project_id, "project_id")
    try:
        db = get_authenticated_client(token)

        proj_res = db.table("projects").select("id").eq("id", project_id).eq("user_id", str(user.id)).execute()
        if not proj_res.data:
            raise HTTPException(status_code=404, detail="Project not found or access denied")

        db.table("projects").delete().eq("id", project_id).execute()
        clear_project_memory(project_id)

        return {"message": "Project and all cascading items deleted successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Delete project failed")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ---------------------------------------------------------------------------
# Documents Endpoints
# ---------------------------------------------------------------------------
@app.get("/documents/{project_id}")
@limiter.limit("120/minute")
def list_documents_endpoint(
    request: Request,
    project_id: str,
    token: str = Depends(get_token),
    user: Any = Depends(get_user),
):
    """List all documents uploaded to a specific project."""
    validate_uuid(project_id, "project_id")
    try:
        db = get_authenticated_client(token)

        proj_res = db.table("projects").select("id").eq("id", project_id).eq("user_id", str(user.id)).execute()
        if not proj_res.data:
            raise HTTPException(status_code=403, detail="Access denied to this project")

        res = db.table("documents").select("*").eq("project_id", project_id).order("created_at", desc=True).execute()
        return res.data or []
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("List documents failed")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/documents/{project_id}/page-text")
@limiter.limit("120/minute")
def get_document_page_text_endpoint(
    request: Request,
    project_id: str,
    filename: str,
    page_num: int,
    token: str = Depends(get_token),
    user: Any = Depends(get_user),
):
    """Retrieve full text of a specific page from document chunks."""
    validate_uuid(project_id, "project_id")
    if not filename or len(filename) > 255:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    if page_num < 1:
        raise HTTPException(status_code=400, detail="Invalid page number.")

    try:
        db = get_authenticated_client(token)

        proj_res = db.table("projects").select("id").eq("id", project_id).eq("user_id", str(user.id)).execute()
        if not proj_res.data:
            raise HTTPException(status_code=403, detail="Access denied to this project")

        # Verify filename belongs to a document in this project
        doc_res = db.table("documents").select("id").eq("project_id", project_id).eq("filename", filename).limit(1).execute()
        if not doc_res.data:
            raise HTTPException(status_code=404, detail="Document not found in this project")

        res = (
            db.table("document_chunks")
            .select("chunk_text, id")
            .eq("project_id", project_id)
            .eq("filename", filename)
            .eq("page_num", page_num)
            .order("id")
            .execute()
        )
        chunks = res.data or []
        if not chunks:
            raise HTTPException(status_code=404, detail="No text chunks found for this page")
        text_list = []
        for c in chunks:
            if isinstance(c, dict):
                text_list.append(str(c.get("chunk_text") or ""))
        full_text = " ".join(text_list)
        return {"filename": filename, "page_num": page_num, "text": full_text}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Retrieve page text failed")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.delete("/documents/{document_id}")
@limiter.limit("60/minute")
def delete_document_endpoint(
    request: Request,
    document_id: str,
    token: str = Depends(get_token),
    user: Any = Depends(get_user),
):
    """Delete a single document and cascade delete its chunks."""
    validate_uuid(document_id, "document_id")
    try:
        db = get_authenticated_client(token)

        doc_res = db.table("documents").select("project_id, filename").eq("id", document_id).execute()
        doc_data = doc_res.data
        if not isinstance(doc_data, list) or not doc_data:
            raise HTTPException(status_code=404, detail="Document not found")
        first_row = doc_data[0]
        if not isinstance(first_row, dict):
            raise HTTPException(status_code=404, detail="Document not found")

        project_id = first_row.get("project_id")
        filename = first_row.get("filename")
        if not project_id or not filename:
            raise HTTPException(status_code=404, detail="Document not found")

        proj_res = db.table("projects").select("id").eq("id", str(project_id)).eq("user_id", str(user.id)).execute()
        if not proj_res.data:
            raise HTTPException(status_code=403, detail="Access denied to delete this document")

        db.table("document_chunks").delete().eq("document_id", document_id).execute()
        db.table("documents").delete().eq("id", document_id).execute()

        return {"message": f"Document '{str(filename)}' deleted successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Delete document failed")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ---------------------------------------------------------------------------
# Background File Processing
# ---------------------------------------------------------------------------
def process_pdf_background_task(temp_path_str: str, filename: str, project_id: str, doc_id: str, user_id: str):
    """FastAPI background task to chunk, embed, and store a PDF document.

    Uses the service client so the task survives even if the user's access token
    expires before processing finishes.
    """
    db = get_service_client()
    try:
        chunk_count = process_and_store_pdf(
            temp_path_str,
            filename,
            project_id,
            document_id=doc_id,
            token=None,  # service client handles authorization
        )
        if chunk_count == 0:
            raise ValueError("PDF contains no selectable text")
        db.table("documents").update({"status": "ready"}).eq("id", doc_id).execute()
        logger.info("Background processing succeeded for file: %s. Chunks: %d", filename, chunk_count)
    except Exception as e:
        logger.exception("Background processing failed for file: %s. Error: %s", filename, str(e))
        db.table("documents").update({"status": "error"}).eq("id", doc_id).execute()
    finally:
        try:
            os.unlink(temp_path_str)
        except Exception:
            pass


@app.post("/upload")
@limiter.limit("10/minute")
async def upload_document_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    project_id: str = Form(...),
    token: str = Depends(get_token),
    user: Any = Depends(get_user),
):
    """Upload PDF file and trigger async background processing."""
    validate_uuid(project_id, "project_id")

    filename = file.filename or "uploaded_document.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF documents are allowed.")

    header = await file.read(4)
    await file.seek(0)
    if header != b"%PDF":
        raise HTTPException(status_code=400, detail="File content is not a valid PDF.")

    db = get_authenticated_client(token)
    proj_res = db.table("projects").select("id").eq("id", project_id).eq("user_id", str(user.id)).execute()
    if not proj_res.data:
        raise HTTPException(status_code=403, detail="Access denied to this project")

    doc_count_res = db.table("documents").select("id", count=CountMethod.exact).eq("project_id", project_id).execute()
    count_val = doc_count_res.count
    existing_count = count_val if count_val is not None else len(cast(List, doc_count_res.data or []))
    if existing_count >= config.MAX_FILES_PER_PROJECT:
        raise HTTPException(status_code=400, detail=f"Maximum limit of {config.MAX_FILES_PER_PROJECT} documents per project reached.")

    contents = await file.read()
    await file.seek(0)
    if len(contents) > config.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum size of {config.MAX_FILE_SIZE_MB}MB.")

    try:
        doc_res = db.table("documents").insert({
            "project_id": project_id,
            "filename": filename,
            "status": "processing",
        }).execute()

        res_data = doc_res.data
        if not isinstance(res_data, list) or not res_data:
            raise HTTPException(status_code=500, detail="Failed to initialize document status in database.")
        first_row = res_data[0]
        if not isinstance(first_row, dict):
            raise HTTPException(status_code=500, detail="Failed to initialize document status in database.")
        doc_id = first_row.get("id")
        if not doc_id:
            raise HTTPException(status_code=500, detail="Failed to initialize document status in database.")

        temp_path = UPLOADS_DIR / f"{project_id}_{uuid.uuid4()}_{filename}"
        temp_path.write_bytes(contents)

        background_tasks.add_task(
            process_pdf_background_task,
            str(temp_path),
            filename,
            project_id,
            str(doc_id),
            str(user.id),
        )

        return {
            "success": True,
            "status": "processing",
            "document_id": str(doc_id),
            "message": "File upload successful. Processing started in the background."
        }

    except Exception as e:
        logger.exception("Upload endpoint error")
        raise HTTPException(status_code=500, detail=f"Failed to initiate file processing: {str(e)}")


# ---------------------------------------------------------------------------
# RAG Chat Endpoint
# ---------------------------------------------------------------------------
@app.post("/ask", response_model=ChatResponse)
@limiter.limit("30/minute")
async def ask_endpoint(
    request: Request,
    req: ChatRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(get_token),
    user: Any = Depends(get_user),
):
    """Perform RAG chat queries against project documents."""
    validate_uuid(req.project_id, "project_id")
    if req.conversation_id:
        validate_uuid(req.conversation_id, "conversation_id")
    message = validate_non_empty_text(req.message, "Message", max_len=2000)

    db = get_authenticated_client(token)
    user_id_str = str(user.id)

    proj_fut = asyncio.to_thread(
        lambda: db.table("projects").select("id")
            .eq("id", req.project_id).eq("user_id", user_id_str).execute()
    )
    proj_res = await proj_fut

    if not proj_res.data:
        raise HTTPException(status_code=403, detail="Access denied to this project")

    allowed, count = await asyncio.to_thread(check_rate_limit, user_id_str, token)
    if not allowed:
        raise HTTPException(status_code=429, detail=f"Daily limit reached ({config.DAILY_QUESTION_LIMIT} questions). Come back tomorrow.")

    try:
        conv_id = req.conversation_id
        if not conv_id:
            conv_res = await asyncio.to_thread(
                lambda: db.table("conversations").insert({
                    "project_id": req.project_id,
                    "title": message[:50]
                }).execute()
            )
            res_data = conv_res.data
            if isinstance(res_data, list) and res_data:
                first_row = res_data[0]
                if isinstance(first_row, dict):
                    conv_id = first_row.get("id")
            if not conv_id:
                raise HTTPException(status_code=500, detail="Failed to create chat conversation.")

        answer, sources = await asyncio.to_thread(
            answer_with_sources, message, req.project_id, "", token
        )

        background_tasks.add_task(
            save_conversation_memory,
            [{"role": "user", "content": message}, {"role": "assistant", "content": answer}],
            user_id=req.project_id
        )
        background_tasks.add_task(
            _save_messages_bg, db, str(conv_id), message, answer, sources
        )

        remaining = max(0, config.DAILY_QUESTION_LIMIT - count)

        return {
            "reply": answer,
            "sources": sources,
            "conversation_id": str(conv_id),
            "remaining_questions": remaining
        }

    except Exception as e:
        logger.exception("Ask endpoint error")
        raise HTTPException(status_code=500, detail=f"Chat generation failure: {str(e)}")


def _save_messages_bg(db, conv_id: str, message: str, answer: str, sources: list) -> None:
    """Background task: persist user + assistant messages to the DB."""
    try:
        db.table("messages").insert([
            {"conversation_id": conv_id, "role": "user",      "content": message, "sources": None},
            {"conversation_id": conv_id, "role": "assistant", "content": answer,  "sources": sources},
        ]).execute()
    except Exception:
        logger.exception("Background message save failed for conversation %s", conv_id)


@app.get("/projects/{project_id}/messages")
@limiter.limit("120/minute")
def get_project_messages(
    request: Request,
    project_id: str,
    limit: int = 50,
    token: str = Depends(get_token),
    user: Any = Depends(get_user),
):
    """Fetch recent messages for the project's last active conversation, with a response limit."""
    validate_uuid(project_id, "project_id")
    limit = max(1, min(limit, 200))
    try:
        db = get_authenticated_client(token)

        proj_res = db.table("projects").select("id").eq("id", project_id).eq("user_id", str(user.id)).execute()
        if not proj_res.data:
            raise HTTPException(status_code=403, detail="Access denied to this project")

        conv_res = db.table("conversations").select("id").eq("project_id", project_id).order("created_at", desc=True).limit(1).execute()
        conv_data = conv_res.data
        if not isinstance(conv_data, list) or not conv_data:
            return {"conversation_id": "", "messages": []}

        first_row = conv_data[0]
        if not isinstance(first_row, dict):
            return {"conversation_id": "", "messages": []}
        conv_id = first_row.get("id")
        if not conv_id:
            return {"conversation_id": "", "messages": []}

        msg_res = db.table("messages").select("role, content, sources").eq("conversation_id", str(conv_id)).order("created_at", desc=False).limit(limit).execute()

        messages = []
        msg_data = msg_res.data
        if isinstance(msg_data, list):
            for m in msg_data:
                if isinstance(m, dict):
                    messages.append({
                        "role": str(m.get("role", "")),
                        "content": str(m.get("content", "")),
                        "sources": cast(List[Dict], m.get("sources") or [])
                    })

        return {"conversation_id": str(conv_id), "messages": messages}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Get messages failed")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.delete("/projects/{project_id}/messages")
@limiter.limit("30/minute")
def clear_project_messages_endpoint(
    request: Request,
    project_id: str,
    token: str = Depends(get_token),
    user: Any = Depends(get_user),
):
    """Clear all chat messages and memory for a specific project."""
    validate_uuid(project_id, "project_id")
    try:
        db = get_authenticated_client(token)

        proj_res = db.table("projects").select("id").eq("id", project_id).eq("user_id", str(user.id)).execute()
        if not proj_res.data:
            raise HTTPException(status_code=403, detail="Access denied to this project")

        clear_project_memory(project_id)
        db.table("conversations").delete().eq("project_id", project_id).execute()

        return {"message": "Chat history and memory cleared successfully."}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Clear project messages failed")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ---------------------------------------------------------------------------
# Public config endpoint
# ---------------------------------------------------------------------------
@app.get("/api/config")
def api_config_endpoint():
    """Expose non-sensitive frontend configuration."""
    return {
        "supabase_url": config.FRONTEND_SUPABASE_URL,
        "supabase_anon_key": config.FRONTEND_SUPABASE_ANON_KEY,
        "max_file_size_mb": config.MAX_FILE_SIZE_MB,
        "max_files_per_project": config.MAX_FILES_PER_PROJECT,
        "daily_question_limit": config.DAILY_QUESTION_LIMIT,
        "gemini_rate_limit_rpm": config.GEMINI_RATE_LIMIT_RPM,
    }


# ---------------------------------------------------------------------------
# Liveness / Health Check
# ---------------------------------------------------------------------------
@app.get("/health")
def health_endpoint():
    """Return health check statistics including database and model details."""
    db_status = "unconfigured"
    if config.SUPABASE_URL and config.SUPABASE_SERVICE_KEY:
        try:
            # Query profiles table with a limit of 1 to verify database connectivity
            client = get_service_client()
            client.table("profiles").select("id").limit(1).execute()
            db_status = "connected"
        except Exception as exc:
            logger.warning("Health check database query failed: %s", exc)
            db_status = f"error: {str(exc)}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "active_model": config.GEMINI_MODEL,
        "embedding_model": config.EMBEDDING_MODEL,
        "gemini_configured": bool(config.GEMINI_API_KEY),
    }


# ---------------------------------------------------------------------------
# Static Files Catch-all (For frontend files when served directly)
# ---------------------------------------------------------------------------
frontend_dir = Path("frontend")
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

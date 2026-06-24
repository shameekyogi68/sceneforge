import asyncio
import logging
import os
import sys
import uuid
from typing import List, Optional, Any, Dict, cast
from pathlib import Path
from postgrest import CountMethod

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Ensure root workspace is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import backend.config as config
from backend.logging_config import setup_logging
from backend.auth import (
    signup, login, get_current_user, check_rate_limit,
    refresh_supabase_token, get_authenticated_client, get_anon_client
)
from backend.rag import answer_with_sources, process_and_store_pdf, delete_project_documents
from backend.memory import get_project_memory, save_conversation_memory, clear_project_memory

# Initialize logging
setup_logging()
logger = logging.getLogger("backend.main")

app = FastAPI(
    title="SceneForge API",
    description="RAG-powered film research assistant API backend",
    version="1.0.0"
)

@app.get("/debug-config")
def debug_config():
    import rxconfig
    return {
        "CORS_ALLOWED_ORIGINS_env": os.getenv("CORS_ALLOWED_ORIGINS"),
        "API_URL_env": os.getenv("API_URL"),
        "SITE_URL_env": os.getenv("SITE_URL"),
        "rxconfig_api_url": getattr(rxconfig.config, "api_url", None),
        "rxconfig_cors_allowed_origins": getattr(rxconfig.config, "cors_allowed_origins", None),
    }

# CORS Middleware Setup
cors_env = os.getenv("CORS_ALLOWED_ORIGINS")
cors_origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()] if cors_env else [
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
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup uploads temp directory
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

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

class ProjectCreateRequest(BaseModel):
    name: str

class ChatRequest(BaseModel):
    message: str
    project_id: str
    conversation_id: Optional[str] = None

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
def auth_signup_endpoint(email: str, password: str):
    """Sign up a new user and return tokens."""
    try:
        res = signup(email, password)
        # Sign up might not return session immediately if email verification is enabled
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
def auth_login_endpoint(email: str, password: str):
    """Authenticate existing user and return tokens."""
    try:
        res = login(email, password)
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
def auth_refresh_endpoint(req: RefreshRequest):
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
def auth_me_endpoint(token: str = Depends(get_token), user: Any = Depends(get_user)):
    """Fetch user profile details and retrieve questions_today, initializing profile if needed."""
    try:
        db = get_authenticated_client(token)
        res = db.table("profiles").select("questions_today").eq("id", str(user.id)).execute()
        today_count = 0
        if not res.data:
            # Initialize profile row for user
            from datetime import date
            today = date.today().isoformat()
            try:
                db.table("profiles").insert({
                    "id": str(user.id),
                    "email": user.email,
                    "questions_today": 0,
                    "last_question_date": today,
                }).execute()
            except Exception:
                pass
        else:
            res_data = res.data
            if isinstance(res_data, list) and res_data:
                row = res_data[0]
                if isinstance(row, dict):
                    today_count = row.get("questions_today", 0)
        return {"id": str(user.id), "email": user.email, "questions_today": today_count}
    except Exception as e:
        logger.exception("Failed to retrieve profile in auth/me")
        return {"id": str(user.id), "email": user.email, "questions_today": 0}

# ---------------------------------------------------------------------------
# Projects Endpoints
# ---------------------------------------------------------------------------

@app.post("/projects")
def create_project_endpoint(req: ProjectCreateRequest, token: str = Depends(get_token), user: Any = Depends(get_user)):
    """Create a new project namespace owned by the user."""
    name = req.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Project name cannot be empty.")
    if len(name) > 120:
        raise HTTPException(status_code=400, detail="Project name must be 120 characters or fewer.")

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
    except Exception as e:
        logger.exception("Create project failed")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/projects")
def list_projects_endpoint(token: str = Depends(get_token), user: Any = Depends(get_user)):
    """List all projects belonging to the authenticated user."""
    try:
        db = get_authenticated_client(token)
        res = db.table("projects").select("*").eq("user_id", str(user.id)).execute()
        data_list = res.data
        projects_list = []
        
        # Safely count documents grouped by project_id
        document_counts = {}
        try:
            docs_res = db.table("documents").select("project_id").execute()
            docs_data = docs_res.data or []
            if isinstance(docs_data, list):
                for d in docs_data:
                    if isinstance(d, dict) and "project_id" in d:
                        pid = d["project_id"]
                        document_counts[pid] = document_counts.get(pid, 0) + 1
        except Exception as exc:
            logger.warning("Could not retrieve document counts: %s", exc)

        if isinstance(data_list, list):
            for p in data_list:
                if isinstance(p, dict):
                    created = str(p.get("created_at", ""))
                    p_copy = dict(p)
                    p_copy["created_date"] = created.split("T")[0] if "T" in created else created
                    p_copy["document_count"] = document_counts.get(p.get("id"), 0)
                    projects_list.append(p_copy)
        return projects_list
    except Exception as e:
        logger.exception("List projects failed")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.delete("/projects/{project_id}")
def delete_project_endpoint(project_id: str, token: str = Depends(get_token), user: Any = Depends(get_user)):
    """Delete a project and clear all related documents and memories."""
    try:
        db = get_authenticated_client(token)
        
        # Verify ownership
        proj_res = db.table("projects").select("id").eq("id", project_id).eq("user_id", str(user.id)).execute()
        if not proj_res.data:
            raise HTTPException(status_code=404, detail="Project not found or access denied")
        
        # Delete project
        db.table("projects").delete().eq("id", project_id).execute()
        
        # Clear mem0 memories for project
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
def list_documents_endpoint(project_id: str, token: str = Depends(get_token), user: Any = Depends(get_user)):
    """List all documents uploaded to a specific project."""
    try:
        db = get_authenticated_client(token)
        
        # Verify project ownership
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
def get_document_page_text_endpoint(
    project_id: str,
    filename: str,
    page_num: int,
    token: str = Depends(get_token),
    user: Any = Depends(get_user)
):
    """Retrieve full text of a specific page from document chunks."""
    try:
        db = get_authenticated_client(token)
        
        # Verify project ownership
        proj_res = db.table("projects").select("id").eq("id", project_id).eq("user_id", str(user.id)).execute()
        if not proj_res.data:
            raise HTTPException(status_code=403, detail="Access denied to this project")
            
        # Retrieve chunks for this document and page
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
def delete_document_endpoint(document_id: str, token: str = Depends(get_token), user: Any = Depends(get_user)):
    """Delete a single document and cascade delete its chunks."""
    try:
        db = get_authenticated_client(token)
        
        # Verify ownership by checking project ownership
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
            
        # Delete document (cascade triggers database deletes on chunks)
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

def process_pdf_background_task(temp_path_str: str, filename: str, project_id: str, doc_id: str, token: str):
    """FastAPI background task to chunk, embed, and store a PDF document."""
    db = get_authenticated_client(token)
    try:
        chunk_count = process_and_store_pdf(
            temp_path_str,
            filename,
            project_id,
            document_id=doc_id,
            token=token
        )
        db.table("documents").update({"status": "ready"}).eq("id", doc_id).execute()
        logger.info("Background processing succeeded for file: %s. Chunks: %d", filename, chunk_count)
    except Exception as e:
        logger.exception("Background processing failed for file: %s", filename)
        db.table("documents").update({"status": "error"}).eq("id", doc_id).execute()
    finally:
        # Cleanup temporary file
        try:
            os.unlink(temp_path_str)
        except Exception:
            pass

@app.post("/upload")
async def upload_document_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    project_id: str = Form(...),
    token: str = Depends(get_token),
    user: Any = Depends(get_user)
):
    """Upload PDF file and trigger async background processing."""
    # 1. Enforce extension check
    filename = file.filename or "uploaded_document.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF documents are allowed.")

    # 2. Magic bytes validation (read first 4 bytes to verify %PDF)
    header = await file.read(4)
    await file.seek(0)
    if header != b"%PDF":
        raise HTTPException(status_code=400, detail="File content is not a valid PDF.")

    # 3. Ownership verification
    db = get_authenticated_client(token)
    proj_res = db.table("projects").select("id").eq("id", project_id).eq("user_id", str(user.id)).execute()
    if not proj_res.data:
        raise HTTPException(status_code=403, detail="Access denied to this project")

    # 4. Limit verification (30 files max)
    doc_count_res = db.table("documents").select("id", count=CountMethod.exact).eq("project_id", project_id).execute()
    count_val = doc_count_res.count
    existing_count = count_val if count_val is not None else len(cast(List, doc_count_res.data or []))
    if existing_count >= config.MAX_FILES_PER_PROJECT:
        raise HTTPException(status_code=400, detail=f"Maximum limit of {config.MAX_FILES_PER_PROJECT} documents per project reached.")

    # 5. File size validation
    contents = await file.read()
    await file.seek(0)
    if len(contents) > config.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum size of {config.MAX_FILE_SIZE_MB}MB.")

    # 6. Save temp file and record doc row in DB
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

        # 7. Queue background processing
        background_tasks.add_task(
            process_pdf_background_task,
            str(temp_path),
            filename,
            project_id,
            str(doc_id),
            token
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
async def ask_endpoint(
    req: ChatRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(get_token),
    user: Any = Depends(get_user)
):
    """Perform RAG chat queries against project documents."""
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    db = get_authenticated_client(token)
    user_id_str = str(user.id)

    # 1. Verify project ownership + fetch memory in parallel
    proj_fut = asyncio.to_thread(
        lambda: db.table("projects").select("id")
            .eq("id", req.project_id).eq("user_id", user_id_str).execute()
    )
    memory_fut = asyncio.to_thread(get_project_memory, req.project_id)

    proj_res, memory = await asyncio.gather(proj_fut, memory_fut)

    if not proj_res.data:
        raise HTTPException(status_code=403, detail="Access denied to this project")

    # 2. Check rate limits
    if not check_rate_limit(user_id_str, token):
        raise HTTPException(status_code=429, detail="Daily limit reached (100 questions). Come back tomorrow.")

    try:
        # 3. Resolve or Create Conversation
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

        # 4. Run RAG Pipeline (memory already fetched in parallel above)
        answer, sources = await asyncio.to_thread(
            answer_with_sources, message, req.project_id, memory, token
        )

        # 5. Save memory + messages in background (do NOT block the response)
        background_tasks.add_task(
            save_conversation_memory,
            [{"role": "user", "content": message}, {"role": "assistant", "content": answer}],
            user_id=req.project_id
        )
        background_tasks.add_task(
            _save_messages_bg, db, str(conv_id), message, answer, sources
        )

        # 6. Compute remaining from rate-limit data already in DB (avoid extra query)
        try:
            profile_res = await asyncio.to_thread(
                lambda: db.table("profiles").select("questions_today")
                    .eq("id", user_id_str).execute()
            )
            data_list = profile_res.data
            today_count = 0
            if isinstance(data_list, list) and len(data_list) > 0:
                row = data_list[0]
                if isinstance(row, dict):
                    raw_val = row.get("questions_today", 0)
                    today_count = int(raw_val) if isinstance(raw_val, (int, float, str)) else 0
        except Exception:
            today_count = 0
        remaining = max(0, config.DAILY_QUESTION_LIMIT - today_count)

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
def get_project_messages(project_id: str, limit: int = 50, token: str = Depends(get_token), user: Any = Depends(get_user)):
    """Fetch recent messages for the project's last active conversation, with a response limit."""
    try:
        db = get_authenticated_client(token)
        
        # Verify project ownership
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
        
        # Structure messages output
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
def clear_project_messages_endpoint(project_id: str, token: str = Depends(get_token), user: Any = Depends(get_user)):
    """Clear all chat messages and memory for a specific project."""
    try:
        db = get_authenticated_client(token)
        
        # Verify project ownership
        proj_res = db.table("projects").select("id").eq("id", project_id).eq("user_id", str(user.id)).execute()
        if not proj_res.data:
            raise HTTPException(status_code=403, detail="Access denied to this project")
            
        # Delete project memory
        clear_project_memory(project_id)
        
        # Delete all conversations belonging to this project (which cascades to messages)
        db.table("conversations").delete().eq("project_id", project_id).execute()
        
        return {"message": "Chat history and memory cleared successfully."}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Clear project messages failed")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ---------------------------------------------------------------------------
# Liveness / Health Check
# ---------------------------------------------------------------------------

@app.get("/health")
def health_endpoint():
    """Return health check statistics."""
    has_gemini = bool(config.GEMINI_API_KEY)
    return {
        "status": "healthy",
        "gemini_configured": has_gemini
    }

# ---------------------------------------------------------------------------
# Static Files Catch-all (For frontend files when served directly)
# ---------------------------------------------------------------------------
frontend_dir = Path("frontend")
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

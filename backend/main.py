import logging
import os
import sys
import uuid
from typing import List, Optional, Any
from pathlib import Path

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

# CORS Middleware Setup
cors_env = os.getenv("CORS_ALLOWED_ORIGINS")
cors_origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()] if cors_env else [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
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
            today_count = 0
        else:
            today_count = res.data[0].get("questions_today", 0)
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
        if not res.data:
            raise HTTPException(status_code=500, detail="Failed to insert project.")
        return res.data[0]
    except Exception as e:
        logger.exception("Create project failed")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/projects")
def list_projects_endpoint(token: str = Depends(get_token), user: Any = Depends(get_user)):
    """List all projects belonging to the authenticated user."""
    try:
        db = get_authenticated_client(token)
        res = db.table("projects").select("*").eq("user_id", str(user.id)).execute()
        data = res.data or []
        for p in data:
            created = p.get("created_at", "")
            p["created_date"] = created.split("T")[0] if "T" in created else created
        return data
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

@app.delete("/documents/{document_id}")
def delete_document_endpoint(document_id: str, token: str = Depends(get_token), user: Any = Depends(get_user)):
    """Delete a single document and cascade delete its chunks."""
    try:
        db = get_authenticated_client(token)
        
        # Verify ownership by checking project ownership
        doc_res = db.table("documents").select("project_id, filename").eq("id", document_id).execute()
        if not doc_res.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        project_id = doc_res.data[0]["project_id"]
        filename = doc_res.data[0]["filename"]
        
        proj_res = db.table("projects").select("id").eq("id", project_id).eq("user_id", str(user.id)).execute()
        if not proj_res.data:
            raise HTTPException(status_code=403, detail="Access denied to delete this document")
            
        # Delete document (cascade triggers database deletes on chunks)
        db.table("document_chunks").delete().eq("document_id", document_id).execute()
        db.table("documents").delete().eq("id", document_id).execute()
        
        return {"message": f"Document '{filename}' deleted successfully"}
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
    if not file.filename.lower().endswith(".pdf"):
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
    doc_count_res = db.table("documents").select("id", count="exact").eq("project_id", project_id).execute()
    existing_count = doc_count_res.count if hasattr(doc_count_res, "count") else len(doc_count_res.data or [])
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
            "filename": file.filename,
            "status": "processing",
        }).execute()
        
        if not doc_res.data:
            raise HTTPException(status_code=500, detail="Failed to initialize document status in database.")
        
        doc_id = doc_res.data[0]["id"]
        
        temp_path = UPLOADS_DIR / f"{project_id}_{uuid.uuid4()}_{file.filename}"
        temp_path.write_bytes(contents)

        # 7. Queue background processing
        background_tasks.add_task(
            process_pdf_background_task,
            str(temp_path),
            file.filename,
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
def ask_endpoint(req: ChatRequest, token: str = Depends(get_token), user: Any = Depends(get_user)):
    """Perform RAG chat queries against project documents."""
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    db = get_authenticated_client(token)

    # 1. Verify project ownership
    proj_res = db.table("projects").select("id").eq("id", req.project_id).eq("user_id", str(user.id)).execute()
    if not proj_res.data:
        raise HTTPException(status_code=403, detail="Access denied to this project")

    # 2. Check rate limits
    if not check_rate_limit(str(user.id), token):
        raise HTTPException(status_code=429, detail="Daily limit reached (100 questions). Come back tomorrow.")

    try:
        # 3. Resolve or Create Conversation
        conv_id = req.conversation_id
        if not conv_id:
            conv_res = db.table("conversations").insert({
                "project_id": req.project_id,
                "title": message[:50]
            }).execute()
            if conv_res.data:
                conv_id = conv_res.data[0]["id"]
            else:
                raise HTTPException(status_code=500, detail="Failed to create chat conversation.")

        # 4. Run RAG Pipeline
        memory = get_project_memory(req.project_id)
        answer, sources = answer_with_sources(message, req.project_id, memory, token=token)

        # 5. Save exchange to Mem0 memory
        save_conversation_memory(
            [
                {"role": "user", "content": message},
                {"role": "assistant", "content": answer}
            ],
            user_id=req.project_id
        )

        # 6. Save message history to DB
        db.table("messages").insert([
            {
                "conversation_id": conv_id,
                "role": "user",
                "content": message,
                "sources": None,
            },
            {
                "conversation_id": conv_id,
                "role": "assistant",
                "content": answer,
                "sources": sources,
            }
        ]).execute()

        # 7. Get remaining question count
        profile_res = db.table("profiles").select("questions_today").eq("id", str(user.id)).execute()
        today_count = profile_res.data[0]["questions_today"] if profile_res.data else 0
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
        if not conv_res.data:
            return {"conversation_id": "", "messages": []}
            
        conv_id = conv_res.data[0]["id"]
        msg_res = db.table("messages").select("role, content, sources").eq("conversation_id", conv_id).order("created_at", asc=True).limit(limit).execute()
        
        # Structure messages output
        messages = []
        for m in (msg_res.data or []):
            messages.append({
                "role": m.get("role", ""),
                "content": m.get("content", ""),
                "sources": m.get("sources") or []
            })
            
        return {"conversation_id": str(conv_id), "messages": messages}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Get messages failed")
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

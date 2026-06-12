import reflex as rx
from typing import List, Dict, Any, Optional
import os
import sys
import uuid
import logging
from datetime import date
from pathlib import Path
from supabase import create_client
from dataclasses import dataclass, field

@dataclass
class SourceItem:
    filename: str
    page: int
    text_preview: str

@dataclass
class ChatMessage:
    role: str
    content: str
    sources: List[SourceItem] = field(default_factory=list)

# Add workspace root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import backend.config as config
from backend.auth import login as auth_login, signup as auth_signup, get_current_user, check_rate_limit
from backend.memory import get_project_memory, save_conversation_memory, clear_project_memory
from backend.rag import answer_with_sources, process_and_store_pdf

logger = logging.getLogger(__name__)

# Ensure uploads folder exists
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)


def get_db(token: str):
    client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    client.postgrest.auth(token)
    return client


class State(rx.State):
    """Global base state containing user authentication tokens in cookies."""
    token: str = rx.Cookie("", name="token")
    user_id: str = rx.Cookie("", name="user_id")
    user_email: str = ""

    @rx.var
    def user_avatar_char(self) -> str:
        """Returns the first uppercase character of the user's email."""
        return self.user_email[0].upper() if self.user_email else "U"


    def check_auth(self) -> Optional[rx.event.EventSpec]:
        """Redirect to login page if token is missing, otherwise retrieve user email."""
        if not self.token:
            return rx.redirect("/login")
        try:
            user = get_current_user(self.token)
            self.user_email = user.email
        except Exception:
            # Token expired or invalid
            return self.logout()

    def logout(self) -> rx.event.EventSpec:
        """Clear tokens and redirect to login."""
        self.token = ""
        self.user_id = ""
        self.user_email = ""
        return rx.redirect("/login")


class AuthState(State):
    """State for email/password signup and login form."""
    email: str = ""
    password: str = ""
    is_signup: bool = False
    error_message: str = ""
    success_message: str = ""
    is_loading: bool = False

    def toggle_mode(self):
        """Toggle between login and signup mode."""
        self.is_signup = not self.is_signup
        self.error_message = ""
        self.success_message = ""

    def handle_auth(self):
        """Submit the login or signup form."""
        self.is_loading = True
        self.error_message = ""
        self.success_message = ""
        
        email_clean = self.email.strip()
        password_clean = self.password
        
        if not email_clean or not password_clean:
            self.error_message = "Email and password are required."
            self.is_loading = False
            return

        try:
            if self.is_signup:
                # Sign up
                result = auth_signup(email_clean, password_clean)
                session = result.session
                if not session:
                    self.success_message = "Check your email to confirm your account before signing in."
                    self.is_loading = False
                    return
                
                self.token = session.access_token
                self.user_id = str(result.user.id)
            else:
                # Login
                result = auth_login(email_clean, password_clean)
                self.token = result.session.access_token
                self.user_id = str(result.user.id)

            self.success_message = "Authenticated successfully! Redirecting..."
            return rx.redirect("/dashboard")
        except Exception as e:
            err_msg = str(e)
            if "Invalid credentials" in err_msg or "401" in err_msg:
                self.error_message = "Invalid email or password."
            else:
                self.error_message = err_msg.replace("HTTPException:", "")
        finally:
            self.is_loading = False

    def login_with_google(self):
        """Redirect to Supabase Google Auth URL."""
        from urllib.parse import urlsplit
        self.error_message = ""
        self.success_message = ""
        try:
            parsed = urlsplit(self.router.url)
            redirect_url = f"{parsed.scheme}://{parsed.netloc}/auth/v1/callback"
            auth_url = f"{config.SUPABASE_URL}/auth/v1/authorize?provider=google&redirect_to={redirect_url}"
            return rx.redirect(auth_url)
        except Exception as e:
            self.error_message = f"Failed to initiate Google sign-in: {e}"

    def handle_callback_load(self):
        """Get the url hash fragment on callback page load."""
        return rx.call_script("window.location.hash", callback=AuthState.process_callback_hash)

    def process_callback_hash(self, hash_str: str):
        """Parse token from hash, set session cookies, and redirect to dashboard."""
        import urllib.parse
        from datetime import date
        
        self.error_message = ""
        self.success_message = ""

        if not hash_str:
            # If no hash (direct visit), redirect to login
            return rx.redirect("/login")

        if hash_str.startswith("#"):
            hash_str = hash_str[1:]
            
        params = urllib.parse.parse_qs(hash_str)
        access_token = params.get("access_token", [None])[0]
        
        if not access_token:
            # Check if there was an error in redirect
            error_desc = params.get("error_description", [None])[0]
            self.error_message = error_desc or "Google authentication failed."
            return rx.redirect("/login")

        try:
            # Validate token and retrieve user details
            user = get_current_user(access_token)
            self.token = access_token
            self.user_id = str(user.id)
            
            # Best-effort profiles upsert
            try:
                db = get_db(access_token)
                db.table("profiles").upsert({
                    "id": str(user.id),
                    "email": user.email,
                    "questions_today": 0,
                    "last_question_date": date.today().isoformat()
                }).execute()
            except Exception as e:
                logger.warning("Could not upsert profile in callback: %s", e)

            self.success_message = "Successfully logged in with Google!"
            return rx.redirect("/dashboard")
            
        except Exception as e:
            logger.exception("Failed to complete Google sign-in callback")
            self.error_message = f"Authentication session verification failed: {e}"
            return rx.redirect("/login")


class DashboardState(State):
    """State for the user projects dashboard."""
    projects: List[Dict[str, Any]] = []
    new_project_name: str = ""
    search_query: str = ""
    is_modal_open: bool = False

    def open_modal(self):
        self.new_project_name = ""
        self.is_modal_open = True

    def close_modal(self):
        self.is_modal_open = False

    def load_projects(self):
        """Fetch all projects owned by the user."""
        if not self.token or not self.user_id:
            return
        try:
            db = get_db(self.token)
            res = db.table("projects").select("*").eq("user_id", self.user_id).execute()
            data = res.data or []
            for p in data:
                created = p.get("created_at", "")
                p["created_date"] = created.split("T")[0] if "T" in created else created
            self.projects = data
        except Exception as e:
            logger.exception("Failed to load projects")
            # If token is invalid/expired, log out
            return self.logout()

    def create_project(self):
        """Insert a new project and reload dashboard."""
        name = self.new_project_name.strip()
        if not name:
            return rx.toast.error("Project name cannot be empty.")
        if len(name) > 120:
            return rx.toast.error("Project name must be 120 characters or fewer.")

        try:
            db = get_db(self.token)
            db.table("projects").insert({
                "id": str(uuid.uuid4()),
                "name": name,
                "user_id": self.user_id,
            }).execute()
            self.is_modal_open = False
            self.new_project_name = ""
            self.load_projects()
            rx.toast.success(f"Project '{name}' created!")
        except Exception as e:
            logger.exception("Failed to create project")
            rx.toast.error(f"Failed to create project: {e}")

    def delete_project(self, project_id: str, project_name: str):
        """Delete a project (with DB cascade) and clear memory."""
        try:
            db = get_db(self.token)
            db.table("projects").delete().eq("id", project_id).eq("user_id", self.user_id).execute()
            clear_project_memory(project_id)
            self.load_projects()
            rx.toast.success(f"Project '{project_name}' deleted.")
        except Exception as e:
            logger.exception("Failed to delete project")
            rx.toast.error(f"Failed to delete project: {e}")

    @rx.var
    def filtered_projects(self) -> List[Dict[str, Any]]:
        """Filter projects list reactively based on search input."""
        q = self.search_query.strip().lower()
        if not q:
            return self.projects
        return [p for p in self.projects if q in p.get("name", "").lower()]


class ProjectState(State):
    """State for a single project's chat workspace and documents."""
    project_id: str = ""
    project_name: str = ""
    documents: List[Dict[str, Any]] = []
    chat_history: List[ChatMessage] = []
    input_message: str = ""
    remaining_questions: str = "100 questions remaining today"
    is_sending: bool = False
    conversation_id: str = ""

    def on_load_project(self):
        """Check authentication and load project data using project_id from router."""
        auth_res = self.check_auth()
        if auth_res:
            return auth_res

        router_params = self.router.page.params
        pid = router_params.get("project_id", "")
        if not pid:
            return rx.redirect("/dashboard")

        self.project_id = pid
        self.load_project_details()

    def load_project_details(self):
        """Query project details, document list, and chat logs from Supabase."""
        try:
            db = get_db(self.token)
            # 1. Fetch project metadata
            proj_res = db.table("projects").select("name").eq("id", self.project_id).eq("user_id", self.user_id).execute()
            if not proj_res.data:
                # Unauthorized or project not found
                return rx.redirect("/dashboard")
            self.project_name = proj_res.data[0]["name"]

            # 2. Fetch document list
            docs_res = db.table("documents").select("*").eq("project_id", self.project_id).order("created_at", desc=True).execute()
            self.documents = docs_res.data or []

            # 3. Fetch remaining question limit
            profile_res = db.table("profiles").select("questions_today").eq("id", self.user_id).execute()
            if profile_res.data:
                today_count = profile_res.data[0]["questions_today"]
                self.remaining_questions = f"{max(0, 100 - today_count)} questions remaining today"
            else:
                self.remaining_questions = "100 questions remaining today"

            # 4. Fetch last active conversation and messages
            conv_res = db.table("conversations").select("id").eq("project_id", self.project_id).order("created_at", desc=True).limit(1).execute()
            if conv_res.data:
                self.conversation_id = conv_res.data[0]["id"]
                msg_res = db.table("messages").select("role, content, sources").eq("conversation_id", self.conversation_id).order("created_at", asc=True).execute()
                self.chat_history = []
                for m in (msg_res.data or []):
                    srcs = []
                    raw_srcs = m.get("sources")
                    if raw_srcs and isinstance(raw_srcs, list):
                        for s in raw_srcs:
                            if isinstance(s, dict):
                                srcs.append(
                                    SourceItem(
                                        filename=s.get("filename", ""),
                                        page=int(s.get("page", 0)),
                                        text_preview=s.get("text_preview", "")
                                    )
                                )
                    self.chat_history.append(
                        ChatMessage(
                            role=m.get("role", ""),
                            content=m.get("content", ""),
                            sources=srcs
                        )
                    )
            else:
                self.conversation_id = ""
                self.chat_history = []

        except Exception as e:
            logger.exception("Failed to load project details")
            rx.toast.error("Failed to load project details.")

    def delete_document(self, doc_id: str, filename: str):
        """Delete document from database and cascade chunks."""
        try:
            db = get_db(self.token)
            db.table("document_chunks").delete().eq("document_id", doc_id).execute()
            db.table("documents").delete().eq("id", doc_id).execute()
            self.load_project_details()
            rx.toast.success(f"Document '{filename}' deleted.")
        except Exception as e:
            logger.exception("Failed to delete document")
            rx.toast.error(f"Failed to delete document: {e}")

    async def handle_upload(self, files: List[rx.UploadFile]):
        """Accept PDF files from rx.upload, process them in backend and save chunk vectors."""
        db = get_db(self.token)
        
        # Verify document limit
        existing_docs_count = len(self.documents)
        if existing_docs_count + len(files) > config.MAX_FILES_PER_PROJECT:
            rx.toast.error(f"Projects can contain at most {config.MAX_FILES_PER_PROJECT} documents.")
            return

        for file in files:
            if not file.filename.lower().endswith(".pdf"):
                rx.toast.error(f"File '{file.filename}' is not a PDF.")
                continue

            # Read file contents and validate size
            contents = await file.read()
            if len(contents) > config.MAX_FILE_SIZE_MB * 1024 * 1024:
                rx.toast.error(f"File '{file.filename}' exceeds the {config.MAX_FILE_SIZE_MB} MB limit.")
                continue

            # Record document metadata as processing
            try:
                doc_res = db.table("documents").insert({
                    "project_id": self.project_id,
                    "filename": file.filename,
                    "status": "processing",
                }).execute()
                
                doc_id = doc_res.data[0]["id"] if doc_res.data else None
                
                # Save temp file
                temp_path = UPLOADS_DIR / f"{self.project_id}_{file.filename}"
                temp_path.write_bytes(contents)

                # Process PDF and store embeddings
                chunk_count = process_and_store_pdf(
                    str(temp_path),
                    file.filename,
                    self.project_id,
                    document_id=doc_id,
                    token=self.token,
                )

                # Update document status to ready
                db.table("documents").update({"status": "ready"}).eq("id", doc_id).execute()
                
                # Cleanup temp file
                temp_path.unlink(missing_ok=True)
                
                rx.toast.success(f"Processed {file.filename}! Created {chunk_count} chunks.")
                
            except Exception as e:
                logger.exception("PDF upload processing failed")
                if 'doc_id' in locals() and doc_id:
                    db.table("documents").update({"status": "error"}).eq("id", doc_id).execute()
                rx.toast.error(f"Failed to process '{file.filename}': {e}")
        
        # Reload details to update sidebar
        self.load_project_details()

    def send_message(self):
        """Send message, perform vector similarity lookup, build prompt, run RAG, and save session memory."""
        message = self.input_message.strip()
        if not message:
            return
        
        self.is_sending = True
        self.input_message = ""
        
        # Add user message to UI immediately for instant feedback
        self.chat_history.append(ChatMessage(role="user", content=message, sources=[]))
        yield

        try:
            db = get_db(self.token)

            # Check rate limiting
            if not check_rate_limit(self.user_id, self.token):
                self.chat_history.append(ChatMessage(
                    role="assistant", 
                    content="⚠️ Daily limit reached (100 questions). Come back tomorrow.",
                    sources=[]
                ))
                self.is_sending = False
                yield
                return

            # Check / Create conversation
            if not self.conversation_id:
                conv_res = db.table("conversations").insert({
                    "project_id": self.project_id,
                    "title": message[:50]
                }).execute()
                if conv_res.data:
                    self.conversation_id = conv_res.data[0]["id"]

            # RAG Answer Generation
            memory = get_project_memory(self.project_id)
            answer, sources = answer_with_sources(message, self.project_id, memory, token=self.token)

            # Save conversations to Mem0 (long-term memory)
            save_conversation_memory(
                [
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": answer}
                ],
                user_id=self.project_id
            )

            # Insert messages into database
            if self.conversation_id:
                db.table("messages").insert([
                    {
                        "conversation_id": self.conversation_id,
                        "role": "user",
                        "content": message,
                        "sources": None,
                    },
                    {
                        "conversation_id": self.conversation_id,
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                ]).execute()

            # Add assistant message and sources to state
            source_items = []
            if sources:
                for s in sources:
                    source_items.append(
                        SourceItem(
                            filename=s.get("filename", ""),
                            page=int(s.get("page", 0)),
                            text_preview=s.get("text_preview", "")
                        )
                    )
            self.chat_history.append(ChatMessage(
                role="assistant",
                content=answer,
                sources=source_items
            ))

            # Reload project details to refresh remaining questions count
            self.load_project_details()

        except Exception as e:
            logger.exception("Failed to send chat message")
            self.chat_history.append(ChatMessage(
                role="assistant",
                content=f"❌ Error generating response: {e}",
                sources=[]
            ))
        finally:
            self.is_sending = False

    def use_example_question(self, text: str):
        """Set input message and send."""
        self.input_message = text
        return ProjectState.send_message()

    def handle_key_down(self, key: str, key_info: Dict[str, bool]):
        """Handle key down event and trigger send message on Enter without Shift."""
        if key == "Enter" and not key_info.get("shift_key", False):
            return ProjectState.send_message()

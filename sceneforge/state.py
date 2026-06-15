import reflex as rx
from typing import List, Dict, Any, Optional
import os
import sys
import uuid
import logging
import asyncio
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
import httpx

logger = logging.getLogger(__name__)

# Ensure uploads folder exists
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")


class State(rx.State):
    """Global base state containing user authentication tokens in cookies."""
    token: str = rx.Cookie("", name="token", secure=True, same_site="strict")
    user_id: str = rx.Cookie("", name="user_id", secure=True, same_site="strict")
    refresh_token: str = rx.Cookie("", name="refresh_token", secure=True, same_site="strict")
    user_email: str = ""

    @rx.var
    def user_avatar_char(self) -> str:
        """Returns the first uppercase character of the user's email."""
        return self.user_email[0].upper() if self.user_email else "U"

    async def _api_request(
        self,
        method: str,
        path: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        auth: bool = True,
        files: Optional[dict] = None,
        data: Optional[dict] = None,
    ) -> httpx.Response:
        """Helper to perform HTTP requests to the FastAPI backend, handling auth and auto token refresh."""
        req_headers = headers.copy() if headers else {}
        if auth and self.token:
            req_headers["Authorization"] = f"Bearer {self.token}"

        from backend.main import app as fastapi_app

        async with httpx.AsyncClient(app=fastapi_app, base_url="http://localhost", timeout=60.0) as client:
            try:
                response = await client.request(
                    method, path, json=json, params=params, headers=req_headers, files=files, data=data
                )
            except httpx.RequestError as exc:
                logger.exception("HTTP Request to backend failed: %s", path)
                raise RuntimeError("Cannot connect to SceneForge backend service.") from exc

            # If 401 and refresh_token exists, try refreshing
            if response.status_code == 401 and auth and self.refresh_token:
                logger.info("Access token expired, attempting refresh...")
                try:
                    refresh_resp = await client.post(
                        "/auth/refresh",
                        json={"refresh_token": self.refresh_token}
                    )
                    if refresh_resp.status_code == 200:
                        refresh_data = refresh_resp.json()
                        self.token = refresh_data["access_token"]
                        self.refresh_token = refresh_data["refresh_token"]
                        
                        # Retry the request with the new access token
                        req_headers["Authorization"] = f"Bearer {self.token}"
                        response = await client.request(
                            method, path, json=json, params=params, headers=req_headers, files=files, data=data
                        )
                    else:
                        logger.warning("Token refresh failed with status %d", refresh_resp.status_code)
                        self.logout()
                except Exception as exc:
                    logger.exception("Token refresh failed with exception")
                    self.logout()

            return response


    async def check_auth(self) -> Optional[rx.event.EventSpec]:
        """Redirect to login page if token is missing, otherwise retrieve user email."""
        if not self.token:
            return rx.redirect("/login")
        try:
            response = await self._api_request("GET", "/auth/me")
            if response.status_code == 200:
                self.user_email = response.json().get("email", "")
            else:
                return self.logout()
        except Exception:
            return self.logout()

    async def check_auth_index(self) -> Optional[rx.event.EventSpec]:
        """Redirect to dashboard if already logged in, otherwise redirect to login."""
        if not self.token:
            return rx.redirect("/login")
        try:
            response = await self._api_request("GET", "/auth/me")
            if response.status_code == 200:
                self.user_email = response.json().get("email", "")
                return rx.redirect("/dashboard")
            else:
                return self.logout()
        except Exception:
            return self.logout()

    async def check_auth_login(self) -> Optional[rx.event.EventSpec]:
        """Redirect to dashboard if already logged in."""
        if self.token:
            try:
                response = await self._api_request("GET", "/auth/me")
                if response.status_code == 200:
                    self.user_email = response.json().get("email", "")
                    return rx.redirect("/dashboard")
            except Exception:
                pass

    def logout(self) -> rx.event.EventSpec:
        """Clear tokens and redirect to login."""
        self.token = ""
        self.user_id = ""
        self.refresh_token = ""
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

    async def handle_auth(self):
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
            path = "/auth/signup" if self.is_signup else "/auth/login"
            response = await self._api_request(
                "POST",
                path,
                params={"email": email_clean, "password": password_clean},
                auth=False
            )
            
            if response.status_code != 200:
                detail = response.json().get("detail", "Authentication failed.")
                raise Exception(detail)
                
            res_data = response.json()
            
            # Sign up might require email confirmation, session is empty
            if self.is_signup and not res_data.get("access_token"):
                self.success_message = "Check your email to confirm your account before signing in."
                return
                
            self.token = res_data["access_token"]
            self.refresh_token = res_data["refresh_token"]
            self.user_id = res_data["user_id"]

            self.success_message = "Authenticated successfully! Redirecting..."
            return rx.redirect("/dashboard")
        except Exception as e:
            logger.exception("Form authentication failed")
            err_msg = str(e)
            if "Invalid email or password" in err_msg or "401" in err_msg or "Invalid credentials" in err_msg:
                self.error_message = "Invalid email or password."
            else:
                self.error_message = err_msg.replace("Exception:", "").strip()
        finally:
            self.is_loading = False

    def login_with_google(self):
        """Redirect to Supabase Google Auth URL."""
        self.error_message = ""
        self.success_message = ""
        try:
            import os

            # Determine base URL
            site_url = os.environ.get("SITE_URL", "").rstrip("/")

            if not site_url:
                try:
                    page_host = str(self.router.page.host or "")
                    if page_host:
                        if "localhost" in page_host or "127.0.0.1" in page_host:
                            site_url = f"http://{page_host}"
                        else:
                            site_url = f"https://{page_host}"
                except Exception:
                    pass

            if not site_url:
                site_url = "https://sceneforge-aqua-ocean.reflex.run"

            redirect_url = f"{site_url}/auth/v1/callback"
            auth_url = (
                f"{config.SUPABASE_URL}/auth/v1/authorize"
                f"?provider=google&redirect_to={redirect_url}"
            )

            logger.info("Redirecting to Supabase OAuth: %s", auth_url)
            return rx.redirect(auth_url)
        except Exception as e:
            logger.exception("Failed to initiate Google sign-in")
            self.error_message = f"Failed to initiate Google sign-in: {e}"

    def handle_callback_load(self):
        """Get the url hash fragment on callback page load."""
        return rx.call_script("window.location.hash", callback=AuthState.process_callback_hash)

    async def process_callback_hash(self, hash_str: str):
        """Parse token from hash, set session cookies, and redirect to dashboard."""
        import urllib.parse
        
        self.error_message = ""
        self.success_message = ""

        if not hash_str:
            # If no hash (direct visit), redirect to login
            return rx.redirect("/login")

        if hash_str.startswith("#"):
            hash_str = hash_str[1:]
            
        params = urllib.parse.parse_qs(hash_str)
        access_token = params.get("access_token", [None])[0]
        ref_token = params.get("refresh_token", [None])[0]
        
        if not access_token:
            # Check if there was an error in redirect
            error_desc = params.get("error_description", [None])[0]
            self.error_message = error_desc or "Google authentication failed."
            return rx.redirect("/login")

        try:
            # Validate token and retrieve user details by calling FastAPI GET /auth/me
            headers = {"Authorization": f"Bearer {access_token}"}
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(f"{BACKEND_URL}/auth/me", headers=headers)
                if res.status_code != 200:
                    raise Exception("Verification with SceneForge backend failed.")
                user_data = res.json()
            
            self.token = access_token
            if ref_token:
                self.refresh_token = ref_token
            self.user_id = user_data["id"]
            self.user_email = user_data["email"]

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
    is_loading: bool = False
    
    # Deletion confirmation dialog state
    project_to_delete_id: str = ""
    project_to_delete_name: str = ""
    is_delete_confirm_open: bool = False

    def open_modal(self):
        self.new_project_name = ""
        self.is_modal_open = True

    def close_modal(self):
        self.is_modal_open = False

    async def load_projects(self):
        """Fetch all projects owned by the user from backend."""
        if not self.token or not self.user_id:
            return
        self.is_loading = True
        yield
        try:
            response = await self._api_request("GET", "/projects")
            if response.status_code == 200:
                self.projects = response.json()
            else:
                self.projects = []
        except Exception as e:
            logger.exception("Failed to load projects")
            yield self.logout()
            return
        finally:
            self.is_loading = False
            yield

    async def create_project(self):
        """Insert a new project via API and reload dashboard."""
        name = self.new_project_name.strip()
        if not name:
            return rx.toast.error("Project name cannot be empty.")
        if len(name) > 120:
            return rx.toast.error("Project name must be 120 characters or fewer.")

        try:
            response = await self._api_request("POST", "/projects", json={"name": name})
            if response.status_code == 200:
                self.is_modal_open = False
                self.new_project_name = ""
                rx.toast.success(f"Project '{name}' created!")
                await self.load_projects()
            else:
                detail = response.json().get("detail", "Failed to create project")
                rx.toast.error(f"Failed to create project: {detail}")
        except Exception as e:
            logger.exception("Failed to create project")
            rx.toast.error("An internal error occurred while creating project.")

    def confirm_delete_project(self, project_id: str, project_name: str):
        """Open delete confirmation modal and store project info."""
        self.project_to_delete_id = project_id
        self.project_to_delete_name = project_name
        self.is_delete_confirm_open = True

    def close_delete_confirm(self):
        """Close delete confirmation modal."""
        self.is_delete_confirm_open = False
        self.project_to_delete_id = ""
        self.project_to_delete_name = ""

    async def execute_delete_project(self):
        """Perform project deletion via backend API."""
        project_id = self.project_to_delete_id
        project_name = self.project_to_delete_name
        if not project_id:
            return

        try:
            response = await self._api_request("DELETE", f"/projects/{project_id}")
            if response.status_code == 200:
                rx.toast.success(f"Project '{project_name}' deleted.")
                self.close_delete_confirm()
                await self.load_projects()
            else:
                detail = response.json().get("detail", "Failed to delete project")
                rx.toast.error(f"Failed to delete project: {detail}")
        except Exception as e:
            logger.exception("Failed to delete project")
            rx.toast.error("An internal error occurred while deleting project.")

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

    async def load_documents(self):
        """Load document list for sidebar."""
        try:
            response = await self._api_request("GET", f"/documents/{self.project_id}")
            if response.status_code == 200:
                self.documents = response.json()
            else:
                self.documents = []
        except Exception:
            logger.exception("Failed to load documents")
            self.documents = []

    async def load_profile(self):
        """Load rate limit information."""
        try:
            response = await self._api_request("GET", "/auth/me")
            if response.status_code == 200:
                today_count = response.json().get("questions_today", 0)
                self.remaining_questions = f"{max(0, 100 - today_count)} questions remaining today"
            else:
                self.remaining_questions = "100 questions remaining today"
        except Exception:
            logger.exception("Failed to load profile details")
            self.remaining_questions = "100 questions remaining today"

    async def load_chat_history(self):
        """Load messages for the last active conversation."""
        try:
            response = await self._api_request("GET", f"/projects/{self.project_id}/messages")
            if response.status_code == 200:
                data = response.json()
                self.conversation_id = data.get("conversation_id", "")
                chat_history = []
                for m in (data.get("messages", []) or []):
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
                    chat_history.append(
                        ChatMessage(
                           role=m.get("role", ""),
                           content=m.get("content", ""),
                           sources=srcs
                        )
                    )
                self.chat_history = chat_history
            else:
                self.conversation_id = ""
                self.chat_history = []
        except Exception:
            logger.exception("Failed to load chat history")
            self.conversation_id = ""
            self.chat_history = []

    async def on_load_project(self):
        """Check authentication and load project data using project_id from router."""
        auth_res = await self.check_auth()
        if auth_res:
            return auth_res

        router_params = self.router.page.params
        pid = router_params.get("project_id", "")
        if not pid:
            return rx.redirect("/dashboard")

        self.project_id = pid
        await self.load_project_details()
        
        # Check if any documents are in 'processing' state on load and start background polling
        any_processing = any(d["status"] == "processing" for d in self.documents)
        if any_processing:
            return ProjectState.start_document_polling

    async def load_project_details(self):
        """Query project details, document list, and chat logs from backend API."""
        try:
            # Verify project details/ownership by listing projects
            response = await self._api_request("GET", "/projects")
            if response.status_code != 200:
                return rx.redirect("/dashboard")
                
            projects = response.json()
            matching = [p for p in projects if p["id"] == self.project_id]
            if not matching:
                # Unauthorized or project not found
                return rx.redirect("/dashboard")
            self.project_name = matching[0]["name"]

            # Load project dependencies
            await self.load_documents()
            await self.load_profile()
            await self.load_chat_history()

        except Exception as e:
            logger.exception("Failed to load project details")
            rx.toast.error("Failed to load project details.")

    async def delete_document(self, doc_id: str, filename: str):
        """Delete document from database and cascade chunks."""
        try:
            response = await self._api_request("DELETE", f"/documents/{doc_id}")
            if response.status_code == 200:
                await self.load_documents()
                rx.toast.success(f"Document '{filename}' deleted.")
            else:
                detail = response.json().get("detail", "Failed to delete document")
                rx.toast.error(f"Failed to delete document: {detail}")
        except Exception as e:
            logger.exception("Failed to delete document")
            rx.toast.error("An internal error occurred while deleting document.")

    async def handle_upload(self, files: List[rx.UploadFile]):
        """Accept PDF files from rx.upload, validate, and send to backend API."""
        # Verify document limit
        existing_docs_count = len(self.documents)
        if existing_docs_count + len(files) > config.MAX_FILES_PER_PROJECT:
            rx.toast.error(f"Projects can contain at most {config.MAX_FILES_PER_PROJECT} documents.")
            return

        has_uploaded_any = False

        for file in files:
            # 1. Extension check
            if not file.filename.lower().endswith(".pdf"):
                rx.toast.error(f"File '{file.filename}' is not a PDF.")
                continue

            # Read file contents
            contents = await file.read()
            
            # 2. Magic bytes check
            if contents[:4] != b"%PDF":
                rx.toast.error(f"File '{file.filename}' is not a valid PDF document.")
                continue

            # 3. Size check
            if len(contents) > config.MAX_FILE_SIZE_MB * 1024 * 1024:
                rx.toast.error(f"File '{file.filename}' exceeds the {config.MAX_FILE_SIZE_MB} MB limit.")
                continue

            # Call FastAPI /upload endpoint using multipart form-data
            try:
                files_payload = {"file": (file.filename, contents, "application/pdf")}
                data_payload = {"project_id": self.project_id}
                
                response = await self._api_request(
                    "POST",
                    "/upload",
                    files=files_payload,
                    data=data_payload
                )
                
                if response.status_code == 200:
                    rx.toast.success(f"File '{file.filename}' uploaded. Processing in background...")
                    has_uploaded_any = True
                else:
                    detail = response.json().get("detail", "Failed to process file")
                    rx.toast.error(f"Failed to process '{file.filename}': {detail}")
            except Exception as e:
                logger.exception("Upload failed")
                rx.toast.error(f"Failed to process '{file.filename}': Server error.")

        if has_uploaded_any:
            await self.load_documents()
            yield ProjectState.start_document_polling

    @rx.background
    async def start_document_polling(self):
        """Background task to poll document processing status until all are completed."""
        while True:
            async with self:
                await self.load_documents()
                any_processing = any(d["status"] == "processing" for d in self.documents)
                if not any_processing:
                    break
            await asyncio.sleep(2.0)

    async def send_message(self):
        """Send message to API, perform RAG, update UI with streamed answers, and refresh rate counts."""
        message = self.input_message.strip()
        if not message:
            return
        
        self.is_sending = True
        self.input_message = ""
        
        # Add user message to UI immediately for instant feedback
        self.chat_history.append(ChatMessage(role="user", content=message, sources=[]))
        yield

        try:
            response = await self._api_request(
                "POST",
                "/ask",
                json={
                    "message": message,
                    "project_id": self.project_id,
                    "conversation_id": self.conversation_id or None
                }
            )

            if response.status_code == 429:
                self.chat_history.append(ChatMessage(
                    role="assistant", 
                    content="⚠️ Daily limit reached (100 questions). Come back tomorrow.",
                    sources=[]
                ))
                self.is_sending = False
                yield
                return
            elif response.status_code != 200:
                detail = response.json().get("detail", "Error generating response.")
                raise Exception(detail)

            res_data = response.json()
            self.conversation_id = res_data["conversation_id"]
            answer = res_data["reply"]
            sources = res_data["sources"]
            remaining_count = res_data["remaining_questions"]
            self.remaining_questions = f"{remaining_count} questions remaining today"

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

        except Exception as e:
            logger.exception("Failed to send chat message")
            self.chat_history.append(ChatMessage(
                role="assistant",
                content="❌ An internal error occurred while generating the response. Please try again later.",
                sources=[]
            ))
        finally:
            self.is_sending = False
            yield

    def use_example_question(self, text: str):
        """Set input message and send."""
        self.input_message = text
        return ProjectState.send_message()

    def handle_key_down(self, key: str, key_info: Dict[str, bool]):
        """Handle key down event and trigger send message on Enter without Shift."""
        if key == "Enter" and not key_info.get("shift_key", False):
            return ProjectState.send_message()

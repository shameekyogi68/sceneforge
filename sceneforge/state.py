import reflex as rx
from typing import List, Dict, Any, Optional, cast
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

# ---------------------------------------------------------------------------
# Module-level persistent HTTP client — avoids TCP handshake on every call.
# Created lazily on first use so the FastAPI ASGI app is fully ready.
# ---------------------------------------------------------------------------
_http_client: Optional[httpx.AsyncClient] = None

def _get_http_client() -> httpx.AsyncClient:
    """Return (or create) the shared async HTTP client with connection pooling."""
    global _http_client
    if _http_client is None or _http_client.is_closed:
        from backend.main import app as fastapi_app
        _http_client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=fastapi_app),
            base_url="http://localhost",
            timeout=60.0,
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=50,
                keepalive_expiry=30,
            ),
        )
    return _http_client


class State(rx.State):
    """Global base state containing user authentication tokens in cookies."""
    token: str = rx.Cookie("", name="token", secure=True, same_site="strict")
    user_id: str = rx.Cookie("", name="user_id", secure=True, same_site="strict")
    refresh_token: str = rx.Cookie("", name="refresh_token", secure=True, same_site="strict")
    user_email: str = ""
    questions_today: int = 0
    router: Any = rx.State.router  # type: ignore

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
        """Helper to perform HTTP requests to the FastAPI backend, handling auth and auto token refresh.
        Uses a module-level persistent client with connection pooling — no TCP handshake per call.
        """
        req_headers = headers.copy() if headers else {}
        if auth and self.token:
            req_headers["Authorization"] = f"Bearer {self.token}"

        client = _get_http_client()
        try:
            response = await client.request(
                method, path, json=json, params=params, headers=req_headers, files=files, data=data
            )
        except httpx.RequestError as exc:
            logger.exception("HTTP Request to backend failed: %s", path)
            raise RuntimeError("Cannot connect to ScriptIQ backend service.") from exc

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
                data = response.json()
                self.user_email = data.get("email", "")
                self.questions_today = data.get("questions_today", 0)
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
                data = response.json()
                self.user_email = data.get("email", "")
                self.questions_today = data.get("questions_today", 0)
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
                    data = response.json()
                    self.user_email = data.get("email", "")
                    self.questions_today = data.get("questions_today", 0)
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
    """State for Google OAuth authentication."""
    error_message: str = ""
    success_message: str = ""
    is_loading: bool = False

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
                    page_host = self.router.page.host or ""
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
        return rx.call_script("window.location.hash", callback=cast(Any, self.process_callback_hash))

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
            # Validate token and retrieve user details using in-process transport
            # (avoids dependency on BACKEND_URL which defaults to localhost and breaks in production)
            req_headers = {"Authorization": f"Bearer {access_token}"}
            client = _get_http_client()
            res = await client.get("/auth/me", headers=req_headers)
            if res.status_code != 200:
                raise Exception("Verification with ScriptIQ backend failed.")
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

    # Explicit setters (replacing deprecated state_auto_setters)
    def set_search_query(self, value: str):
        self.search_query = value

    def set_new_project_name(self, value: str):
        self.new_project_name = value

    def set_is_modal_open(self, value: bool):
        self.is_modal_open = value

    def set_is_delete_confirm_open(self, value: bool):
        self.is_delete_confirm_open = value

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
            yield rx.toast.error("Project name cannot be empty.")
            return
        if len(name) > 120:
            yield rx.toast.error("Project name must be 120 characters or fewer.")
            return

        try:
            response = await self._api_request("POST", "/projects", json={"name": name})
            if response.status_code == 200:
                self.is_modal_open = False
                self.new_project_name = ""
                rx.toast.success(f"Project '{name}' created!")
                yield self.load_projects()
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
                yield self.load_projects()
            else:
                detail = response.json().get("detail", "Failed to delete project")
                rx.toast.error(f"Failed to delete project: {detail}")
        except Exception as e:
            logger.exception("Failed to delete project")
            rx.toast.error("An internal error occurred while deleting project.")

    @rx.var(cache=True)
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
    is_sending: bool = False
    conversation_id: str = ""
    doc_steps: Dict[str, int] = {}

    # Preview/Inspector state
    selected_preview_filename: str = ""
    selected_preview_page: int = 1
    selected_preview_text: str = ""
    selected_preview_highlight: str = ""
    is_preview_modal_open: bool = False
    is_preview_loading: bool = False

    # Explicit setter (replacing deprecated state_auto_setters)
    def set_input_message(self, value: str):
        self.input_message = value

    @rx.var
    def remaining_questions(self) -> str:
        """Compute remaining questions dynamically from state."""
        return f"{max(0, 100 - self.questions_today)} questions remaining today"

    async def load_documents(self):
        """Load document list for sidebar."""
        try:
            response = await self._api_request("GET", f"/documents/{self.project_id}")
            if response.status_code == 200:
                self.documents = response.json()
                # Initialize simulated steps for any document that is processing
                for d in self.documents:
                    d_id = str(d.get("id", ""))
                    if d.get("status") == "processing" and d_id not in self.doc_steps:
                        self.doc_steps[d_id] = 1
            else:
                self.documents = []
        except Exception:
            logger.exception("Failed to load documents")
            self.documents = []

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
            # Load project details securely
            response = await self._api_request("GET", f"/projects/{self.project_id}")
            if response.status_code != 200:
                return rx.redirect("/dashboard")
                
            project_data = response.json()
            self.project_name = project_data["name"]

            # Load project dependencies concurrently
            await asyncio.gather(
                self.load_documents(),
                self.load_chat_history()
            )

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
            if not file.filename or not file.filename.lower().endswith(".pdf"):
                rx.toast.error(f"File '{file.filename or 'Unnamed'}' is not a PDF.")
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

    @rx.event(background=True)
    async def start_document_polling(self):
        """Background task to poll document processing status until all are completed."""
        while True:
            async with self:
                await self.load_documents()
                # Increment steps for documents that are still processing
                for d in self.documents:
                    d_id = str(d.get("id", ""))
                    if d.get("status") == "processing":
                        current_step = self.doc_steps.get(d_id, 1)
                        if current_step < 3:
                            self.doc_steps[d_id] = current_step + 1
                    elif d_id in self.doc_steps:
                        # Clean up completed documents
                        del self.doc_steps[d_id]
                
                any_processing = any(d["status"] == "processing" for d in self.documents)
                if not any_processing:
                    break
            await asyncio.sleep(3.0)

    async def send_message(self):
        """Send message to API, perform RAG, update UI with streamed answers, and refresh rate counts."""
        message = self.input_message.strip()
        if not message:
            return
        
        self.is_sending = True
        self.input_message = ""
        
        # Add user message to UI immediately for instant feedback
        self.chat_history.append(ChatMessage(role="user", content=message, sources=[]))
        yield ProjectState.scroll_to_bottom

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
                yield ProjectState.scroll_to_bottom
                return
            elif response.status_code != 200:
                detail = response.json().get("detail", "Error generating response.")
                raise Exception(detail)

            res_data = response.json()
            self.conversation_id = res_data["conversation_id"]
            answer = res_data["reply"]
            sources = res_data["sources"]
            remaining_count = res_data["remaining_questions"]
            self.questions_today = 100 - remaining_count

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
            yield ProjectState.scroll_to_bottom

    def use_example_question(self, text: str):
        """Set input message and send."""
        self.input_message = text
        return self.send_message()

    def handle_key_down(self, key: str, key_info: Dict[str, bool]):
        """Handle key down event and trigger send message on Enter without Shift."""
        if key == "Enter" and not key_info.get("shift_key", False):
            return self.send_message()

    def set_is_preview_modal_open(self, val: bool):
        self.is_preview_modal_open = val

    def close_preview_modal(self):
        self.is_preview_modal_open = False
        self.selected_preview_filename = ""
        self.selected_preview_text = ""
        self.selected_preview_highlight = ""

    async def open_document_preview(self, filename: str, page_num: int, highlight_text: str = ""):
        """Fetch and display preview of a specific document page."""
        # Ensure document is ready before opening preview
        doc_ready = False
        for doc in self.documents:
            if doc.get("filename") == filename:
                if doc.get("status") == "ready":
                    doc_ready = True
                break
        if not doc_ready:
            return

        self.selected_preview_filename = filename
        self.selected_preview_page = page_num
        self.selected_preview_highlight = highlight_text
        self.is_preview_loading = True
        self.selected_preview_text = "Fetching document page text..."
        self.is_preview_modal_open = True
        yield

        try:
            response = await self._api_request(
                "GET",
                f"/documents/{self.project_id}/page-text",
                params={"filename": filename, "page_num": page_num}
            )
            if response.status_code == 200:
                raw_text = response.json().get("text", "")
                
                import html
                # Escape HTML characters to protect against XSS or formatting breaks from PDF content
                escaped_text = html.escape(raw_text)
                
                if self.selected_preview_highlight:
                    # Clean the citation snippet
                    clean_highlight = self.selected_preview_highlight.replace("...", "").strip()
                    if clean_highlight and len(clean_highlight) >= 5:
                        import re
                        try:
                            # Safely escape regex characters in search phrase
                            pattern = re.escape(clean_highlight)
                            # Wrap matching string in mark tags
                            escaped_text = re.sub(
                                pattern,
                                lambda m: f'<mark class="search-highlight">{m.group(0)}</mark>',
                                escaped_text,
                                flags=re.IGNORECASE
                            )
                        except Exception:
                            pass
                self.selected_preview_text = escaped_text
            else:
                detail = response.json().get("detail", "Failed to load document text.")
                self.selected_preview_text = f"Error: {detail}"
        except Exception as e:
            logger.exception("Failed to open document preview")
            self.selected_preview_text = "An error occurred while loading page text."
        finally:
            self.is_preview_loading = False
            yield

    async def scroll_to_bottom(self):
        """Scroll chat container to bottom smoothly."""
        yield rx.call_script(
            "const el = document.getElementById('chat-scroll-container'); "
            "if (el) { el.scrollTop = el.scrollHeight; }"
        )

    async def clear_chat(self):
        """Delete conversation messages and memory for the current project."""
        try:
            response = await self._api_request("DELETE", f"/projects/{self.project_id}/messages")
            if response.status_code == 200:
                self.chat_history = []
                self.conversation_id = ""
                rx.toast.success("Chat history cleared.")
            else:
                detail = response.json().get("detail", "Failed to clear chat history.")
                rx.toast.error(f"Error: {detail}")
        except Exception as e:
            logger.exception("Failed to clear chat")
            rx.toast.error("An error occurred while clearing chat.")
        yield

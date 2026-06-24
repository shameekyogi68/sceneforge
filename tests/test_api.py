import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import io

# Add workspace to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["GEMINI_API_KEY"] = "dummy_key"
os.environ["SUPABASE_URL"] = "https://dummy.supabase.co"
os.environ["SUPABASE_KEY"] = "dummy_anon_key"

with patch("supabase.create_client") as mock_create:
    mock_create.return_value = MagicMock()
    from fastapi.testclient import TestClient
    from backend.main import app

class TestApi(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        
        # Setup dummy user
        self.dummy_user = MagicMock()
        self.dummy_user.id = "user-123"
        self.dummy_user.email = "test@example.com"

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")
        self.assertTrue(response.json()["gemini_configured"])

    @patch("backend.main.signup")
    def test_signup_endpoint(self, mock_signup):
        mock_res = MagicMock()
        mock_res.user.id = "user-123"
        mock_res.session.access_token = "access-token"
        mock_res.session.refresh_token = "refresh-token"
        mock_signup.return_value = mock_res
        
        response = self.client.post("/auth/signup", json={"email": "test@example.com", "password": "password123"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["access_token"], "access-token")
        self.assertEqual(data["refresh_token"], "refresh-token")
        self.assertEqual(data["user_id"], "user-123")

    @patch("backend.main.login")
    def test_login_endpoint(self, mock_login):
        mock_res = MagicMock()
        mock_res.user.id = "user-123"
        mock_res.session.access_token = "access-token"
        mock_res.session.refresh_token = "refresh-token"
        mock_login.return_value = mock_res
        
        response = self.client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["access_token"], "access-token")
        self.assertEqual(data["user_id"], "user-123")

    @patch("backend.main.refresh_supabase_token")
    def test_refresh_endpoint(self, mock_refresh):
        mock_refresh.return_value = ("new-access", "new-refresh")
        
        response = self.client.post("/auth/refresh", json={"refresh_token": "old-refresh"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["access_token"], "new-access")
        self.assertEqual(data["refresh_token"], "new-refresh")

    @patch("backend.main.get_current_user")
    @patch("backend.main.get_authenticated_client")
    def test_get_me_endpoint(self, mock_get_db, mock_get_user):
        mock_get_user.return_value = self.dummy_user
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Mock select query returning user profile questions count
        mock_select_res = MagicMock()
        mock_select_res.data = [{"questions_today": 35}]
        mock_db.table().select().eq().execute.return_value = mock_select_res
        
        headers = {"Authorization": "Bearer dummy-token"}
        response = self.client.get("/auth/me", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], "user-123")
        self.assertEqual(data["email"], "test@example.com")
        self.assertEqual(data["questions_today"], 35)

    @patch("backend.main.get_current_user")
    @patch("backend.main.get_authenticated_client")
    def test_create_project(self, mock_get_db, mock_get_user):
        mock_get_user.return_value = self.dummy_user
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_insert_res = MagicMock()
        mock_insert_res.data = [{"id": "proj-111", "name": "FilmTest", "user_id": "user-123"}]
        mock_db.table().insert().execute.return_value = mock_insert_res
        
        headers = {"Authorization": "Bearer dummy-token"}
        response = self.client.post("/projects", json={"name": "FilmTest"}, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], "proj-111")
        self.assertEqual(data["name"], "FilmTest")

    @patch("backend.main.get_current_user")
    @patch("backend.main.get_authenticated_client")
    def test_list_projects(self, mock_get_db, mock_get_user):
        mock_get_user.return_value = self.dummy_user
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        mock_select_res = MagicMock()
        mock_select_res.data = [
            {"id": "proj-1", "name": "Project Alpha", "created_at": "2026-06-15T10:00:00Z"},
            {"id": "proj-2", "name": "Project Beta", "created_at": "2026-06-15T12:00:00Z"}
        ]
        mock_db.table().select().eq().execute.return_value = mock_select_res
        
        headers = {"Authorization": "Bearer dummy-token"}
        response = self.client.get("/projects", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "Project Alpha")
        self.assertEqual(data[0]["created_date"], "2026-06-15")

    @patch("backend.main.get_current_user")
    @patch("backend.main.get_authenticated_client")
    def test_list_projects_with_document_counts(self, mock_get_db, mock_get_user):
        mock_get_user.return_value = self.dummy_user
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Mock table specifically depending on arguments to list document counts
        mock_projects_table = MagicMock()
        mock_documents_table = MagicMock()
        
        def table_side_effect(table_name):
            if table_name == "projects":
                return mock_projects_table
            elif table_name == "documents":
                return mock_documents_table
            return MagicMock()
            
        mock_db.table.side_effect = table_side_effect
        
        # Set up projects table query mock
        mock_projects_select_res = MagicMock()
        mock_projects_select_res.data = [
            {"id": "proj-1", "name": "Project Alpha", "created_at": "2026-06-15T10:00:00Z"},
            {"id": "proj-2", "name": "Project Beta", "created_at": "2026-06-15T12:00:00Z"}
        ]
        mock_projects_table.select.return_value.eq.return_value.execute.return_value = mock_projects_select_res
        
        # Set up documents table query mock
        mock_documents_select_res = MagicMock()
        mock_documents_select_res.data = [
            {"project_id": "proj-1"},
            {"project_id": "proj-1"},
            {"project_id": "proj-2"}
        ]
        mock_documents_table.select.return_value.in_.return_value.execute.return_value = mock_documents_select_res
        
        headers = {"Authorization": "Bearer dummy-token"}
        response = self.client.get("/projects", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "Project Alpha")
        self.assertEqual(data[0]["document_count"], 2)
        self.assertEqual(data[1]["name"], "Project Beta")
        self.assertEqual(data[1]["document_count"], 1)

    @patch("backend.main.get_current_user")
    @patch("backend.main.get_authenticated_client")
    @patch("backend.main.clear_project_memory")
    def test_delete_project(self, mock_clear_mem, mock_get_db, mock_get_user):
        mock_get_user.return_value = self.dummy_user
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Mock project ownership check succeeds
        mock_select_res = MagicMock()
        mock_select_res.data = [{"id": "proj-1"}]
        mock_db.table().select().eq().eq().execute.return_value = mock_select_res
        
        headers = {"Authorization": "Bearer dummy-token"}
        response = self.client.delete("/projects/proj-1", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Project and all cascading items deleted successfully")
        mock_clear_mem.assert_called_with("proj-1")

    @patch("backend.main.get_current_user")
    @patch("backend.main.get_authenticated_client")
    def test_list_documents(self, mock_get_db, mock_get_user):
        mock_get_user.return_value = self.dummy_user
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Mock project ownership check
        mock_proj_res = MagicMock()
        mock_proj_res.data = [{"id": "proj-1"}]
        
        # Mock documents select query
        mock_doc_res = MagicMock()
        mock_doc_res.data = [
            {"id": "doc-1", "filename": "script.pdf", "status": "ready"},
            {"id": "doc-2", "filename": "research.pdf", "status": "processing"}
        ]
        
        mock_db.table().select().eq().eq().execute.return_value = mock_proj_res
        mock_db.table().select().eq().order().execute.return_value = mock_doc_res
        
        headers = {"Authorization": "Bearer dummy-token"}
        response = self.client.get("/documents/proj-1", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(response.json()[0]["filename"], "script.pdf")

    @patch("backend.main.get_current_user")
    @patch("backend.main.get_authenticated_client")
    def test_delete_document(self, mock_get_db, mock_get_user):
        mock_get_user.return_value = self.dummy_user
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Mock document query returning project_id
        mock_doc_res = MagicMock()
        mock_doc_res.data = [{"project_id": "proj-1", "filename": "script.pdf"}]
        mock_db.table().select().eq().execute.return_value = mock_doc_res
        
        # Mock project ownership check succeeds
        mock_proj_res = MagicMock()
        mock_proj_res.data = [{"id": "proj-1"}]
        mock_db.table().select().eq().eq().execute.return_value = mock_proj_res
        
        headers = {"Authorization": "Bearer dummy-token"}
        response = self.client.delete("/documents/doc-1", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Document 'script.pdf' deleted successfully")

    @patch("backend.main.get_current_user")
    @patch("backend.main.get_authenticated_client")
    @patch("backend.main.process_pdf_background_task")
    def test_upload_document_success(self, mock_bg_task, mock_get_db, mock_get_user):
        mock_get_user.return_value = self.dummy_user
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        # 1. Project ownership mock
        mock_proj_res = MagicMock()
        mock_proj_res.data = [{"id": "proj-1"}]
        mock_db.table().select().eq().eq().execute.return_value = mock_proj_res
        
        # 2. Document count check mock (under limit of 30)
        mock_count_res = MagicMock()
        mock_count_res.count = 5
        mock_count_res.data = []
        mock_db.table().select().eq().execute.return_value = mock_count_res
        
        # 3. Document insertion mock
        mock_insert_res = MagicMock()
        mock_insert_res.data = [{"id": "new-doc-id"}]
        mock_db.table().insert().execute.return_value = mock_insert_res
        
        pdf_content = b"%PDF-1.4\n%..."
        file_data = {"file": ("script.pdf", io.BytesIO(pdf_content), "application/pdf")}
        data_data = {"project_id": "proj-1"}
        
        headers = {"Authorization": "Bearer dummy-token"}
        
        # Disable file cleanup in test upload directory
        with patch("os.unlink") as mock_unlink:
            response = self.client.post("/upload", files=file_data, data=data_data, headers=headers)
            
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json()["document_id"], "new-doc-id")

    @patch("backend.main.get_current_user")
    @patch("backend.main.get_authenticated_client")
    def test_upload_document_invalid_magic_bytes(self, mock_get_db, mock_get_user):
        mock_get_user.return_value = self.dummy_user
        
        # Plain text content instead of %PDF magic bytes
        invalid_content = b"This is not a PDF file."
        file_data = {"file": ("script.pdf", io.BytesIO(invalid_content), "application/pdf")}
        data_data = {"project_id": "proj-1"}
        
        headers = {"Authorization": "Bearer dummy-token"}
        response = self.client.post("/upload", files=file_data, data=data_data, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("content is not a valid PDF", response.json()["detail"])

    @patch("backend.main.get_current_user")
    @patch("backend.main.get_authenticated_client")
    @patch("backend.main.check_rate_limit")
    @patch("backend.main.answer_with_sources")
    @patch("backend.main.save_conversation_memory")
    def test_ask_endpoint_success(self, mock_save_mem, mock_answer, mock_rate_limit, mock_get_db, mock_get_user):
        mock_get_user.return_value = self.dummy_user
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Rate limit passes
        mock_rate_limit.return_value = (True, 3)
        
        # Project ownership check
        mock_proj_res = MagicMock()
        mock_proj_res.data = [{"id": "proj-1"}]
        mock_db.table().select().eq().eq().execute.return_value = mock_proj_res
        
        # Conversation creation/selection mock
        mock_conv_res = MagicMock()
        mock_conv_res.data = [{"id": "conv-789"}]
        mock_db.table().insert().execute.return_value = mock_conv_res
        
        # RAG Pipeline mocks
        mock_answer.return_value = ("The answer is here.", [{"filename": "doc.pdf", "page": 2, "text_preview": "some preview"}])
        
        # Profile check for remaining questions
        mock_profile_res = MagicMock()
        mock_profile_res.data = [{"questions_today": 3}]
        mock_db.table().select().eq().execute.return_value = mock_profile_res
        
        headers = {"Authorization": "Bearer dummy-token"}
        chat_request = {
            "message": "Where is the scene shot?",
            "project_id": "proj-1",
            "conversation_id": None
        }
        response = self.client.post("/ask", json=chat_request, headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["reply"], "The answer is here.")
        self.assertEqual(data["conversation_id"], "conv-789")
        self.assertEqual(data["remaining_questions"], 97) # 100 - 3

    @patch("backend.main.get_current_user")
    @patch("backend.main.get_authenticated_client")
    @patch("backend.main.check_rate_limit")
    def test_ask_endpoint_rate_limited(self, mock_rate_limit, mock_get_db, mock_get_user):
        mock_get_user.return_value = self.dummy_user
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Rate limit hit -> returns False
        mock_rate_limit.return_value = (False, 100)
        
        # Project ownership check
        mock_proj_res = MagicMock()
        mock_proj_res.data = [{"id": "proj-1"}]
        mock_db.table().select().eq().eq().execute.return_value = mock_proj_res
        
        headers = {"Authorization": "Bearer dummy-token"}
        chat_request = {
            "message": "Where is the scene shot?",
            "project_id": "proj-1",
            "conversation_id": None
        }
        response = self.client.post("/ask", json=chat_request, headers=headers)
        
        self.assertEqual(response.status_code, 429)
        self.assertIn("Daily limit reached", response.json()["detail"])

    @patch("backend.main.get_current_user")
    @patch("backend.main.get_authenticated_client")
    def test_get_document_page_text_success(self, mock_get_db, mock_get_user):
        mock_get_user.return_value = self.dummy_user
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Project ownership mock
        mock_proj_res = MagicMock()
        mock_proj_res.data = [{"id": "proj-1"}]
        mock_db.table().select().eq().eq().execute.return_value = mock_proj_res

        # Chunks query mock
        mock_chunks_res = MagicMock()
        mock_chunks_res.data = [
            {"chunk_text": "First chunk on page 4.", "id": 10},
            {"chunk_text": "Second chunk on page 4.", "id": 11}
        ]
        # Chunks select query chain
        mock_db.table().select().eq().eq().eq().order().execute.return_value = mock_chunks_res

        headers = {"Authorization": "Bearer dummy-token"}
        response = self.client.get("/documents/proj-1/page-text?filename=c.pdf&page_num=4", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["filename"], "c.pdf")
        self.assertEqual(data["page_num"], 4)
        self.assertEqual(data["text"], "First chunk on page 4. Second chunk on page 4.")

    @patch("backend.main.get_current_user")
    @patch("backend.main.get_authenticated_client")
    @patch("backend.main.clear_project_memory")
    def test_clear_project_messages_success(self, mock_clear_mem, mock_get_db, mock_get_user):
        mock_get_user.return_value = self.dummy_user
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Project ownership mock
        mock_proj_res = MagicMock()
        mock_proj_res.data = [{"id": "proj-1"}]
        mock_db.table().select().eq().eq().execute.return_value = mock_proj_res

        headers = {"Authorization": "Bearer dummy-token"}
        response = self.client.delete("/projects/proj-1/messages", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Chat history and memory cleared successfully.")
        mock_clear_mem.assert_called_once_with("proj-1")
        mock_db.table().delete().eq().execute.assert_called_once()

if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add workspace to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the environment variables before main import
os.environ["GEMINI_API_KEY"] = "dummy_key"
os.environ["SUPABASE_URL"] = "https://dummy.supabase.co"
os.environ["SUPABASE_KEY"] = "dummy_anon_key"

# We must mock supabase.create_client at the very top before any app imports
with patch("supabase.create_client") as mock_create_client, \
     patch("google.generativeai.configure"), \
     patch("google.generativeai.GenerativeModel"):
     
    # Setup mock supabase client response
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client
    
    from backend.main import app
    from fastapi.testclient import TestClient

class TestApi(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy", "gemini_configured": True})

    def test_api_config(self):
        response = self.client.get("/api/config")
        self.assertEqual(response.status_code, 200)
        config_data = response.json()
        self.assertIn("supabase_url", config_data)
        self.assertIn("supabase_anon_key", config_data)

    def test_upload_non_pdf_rejected(self):
        # We need to simulate auth. Let's patch get_current_user to return a dummy user.
        with patch("backend.main.get_current_user") as mock_get_user, \
             patch("backend.main.get_token") as mock_get_token:
            
            mock_get_user.return_value = MagicMock(id="user-123")
            mock_get_token.return_value = "token-123"
            
            # Send txt file
            files = {"file": ("test.txt", b"hello world", "text/plain")}
            response = self.client.post(
                "/upload", 
                files=files, 
                data={"project_id": "proj-123"},
                headers={"Authorization": "Bearer token-123"}
            )
            self.assertEqual(response.status_code, 400)
            self.assertIn("Only PDF files are accepted", response.json()["detail"])

    def test_ask_empty_message_rejected(self):
        with patch("backend.main.get_current_user") as mock_get_user, \
             patch("backend.main.get_token") as mock_get_token:
            
            mock_get_user.return_value = MagicMock(id="user-123")
            mock_get_token.return_value = "token-123"
            
            # Message is empty
            response = self.client.post(
                "/ask", 
                params={"message": "   ", "project_id": "proj-123"},
                headers={"Authorization": "Bearer token-123"}
            )
            self.assertEqual(response.status_code, 400)
            self.assertIn("Message cannot be empty", response.json()["detail"])

if __name__ == "__main__":
    unittest.main()

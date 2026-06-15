import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from datetime import date

# Add workspace to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["GEMINI_API_KEY"] = "dummy_key"
os.environ["SUPABASE_URL"] = "https://dummy.supabase.co"
os.environ["SUPABASE_KEY"] = "dummy_anon_key"

# We will mock create_client before importing to prevent initial connections
with patch("supabase.create_client") as mock_create_client:
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client
    from backend.auth import (
        ClientCache,
        signup,
        login,
        get_current_user,
        refresh_supabase_token,
        check_rate_limit,
        get_anon_client,
    )
    import backend.config as config

class TestAuth(unittest.TestCase):

    def setUp(self):
        # Reset the global cached anon client
        import backend.auth
        backend.auth._anon_client = None

    @patch("backend.auth.create_client")
    def test_client_cache_basic(self, mock_create):
        mock_c1 = MagicMock()
        mock_c2 = MagicMock()
        mock_create.side_effect = [mock_c1, mock_c2]
        
        cache = ClientCache(max_size=2)
        
        # Get with empty token -> returns anon client
        with patch("backend.auth.get_anon_client") as mock_anon:
            mock_anon_val = MagicMock()
            mock_anon.return_value = mock_anon_val
            self.assertEqual(cache.get(""), mock_anon_val)
            
        # Get with token1 -> creates and caches client
        c1 = cache.get("token1")
        self.assertEqual(c1, mock_c1)
        mock_c1.postgrest.auth.assert_called_with("token1")
        
        # Get token1 again -> hits cache
        c1_again = cache.get("token1")
        self.assertEqual(c1_again, mock_c1)
        self.assertEqual(mock_create.call_count, 1)

        # Get token2 -> creates and caches
        c2 = cache.get("token2")
        self.assertEqual(c2, mock_c2)
        self.assertEqual(mock_create.call_count, 2)

    @patch("backend.auth.create_client")
    def test_client_cache_lru_eviction(self, mock_create):
        mock_c1 = MagicMock()
        mock_c2 = MagicMock()
        mock_c3 = MagicMock()
        mock_create.side_effect = [mock_c1, mock_c2, mock_c3]
        
        cache = ClientCache(max_size=2)
        cache.get("token1")
        cache.get("token2")
        
        # Access token1 to make token2 LRU
        cache.get("token1")
        
        # Add token3 -> should evict token2
        cache.get("token3")
        
        self.assertIn("token1", cache.cache)
        self.assertIn("token3", cache.cache)
        self.assertNotIn("token2", cache.cache)

    @patch("backend.auth.get_anon_client")
    def test_signup_success(self, mock_anon):
        mock_client = MagicMock()
        mock_anon.return_value = mock_client
        
        mock_user = MagicMock()
        mock_user.id = "user123"
        mock_signup_res = MagicMock()
        mock_signup_res.user = mock_user
        mock_client.auth.sign_up.return_value = mock_signup_res
        
        res = signup("test@example.com", "password123")
        
        self.assertEqual(res.user.id, "user123")
        mock_client.auth.sign_up.assert_called_with({"email": "test@example.com", "password": "password123"})
        mock_client.table.assert_called_with("profiles")
        mock_client.table().insert.assert_called()

    @patch("backend.auth.get_anon_client")
    def test_signup_failure(self, mock_anon):
        mock_client = MagicMock()
        mock_anon.return_value = mock_client
        mock_client.auth.sign_up.side_effect = Exception("Signup Error")
        
        from fastapi import HTTPException
        with self.assertRaises(HTTPException) as context:
            signup("test@example.com", "password")
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Signup Error", context.exception.detail)

    @patch("backend.auth.get_anon_client")
    def test_login_success(self, mock_anon):
        mock_client = MagicMock()
        mock_anon.return_value = mock_client
        
        mock_session = MagicMock()
        mock_login_res = MagicMock()
        mock_login_res.session = mock_session
        mock_client.auth.sign_in_with_password.return_value = mock_login_res
        
        res = login("test@example.com", "password")
        self.assertEqual(res.session, mock_session)
        mock_client.auth.sign_in_with_password.assert_called_with({"email": "test@example.com", "password": "password"})

    @patch("backend.auth.get_anon_client")
    def test_login_failure(self, mock_anon):
        mock_client = MagicMock()
        mock_anon.return_value = mock_client
        mock_client.auth.sign_in_with_password.side_effect = Exception("Auth fail")
        
        from fastapi import HTTPException
        with self.assertRaises(HTTPException) as context:
            login("test@example.com", "password")
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Invalid email or password")

    @patch("backend.auth.get_anon_client")
    def test_get_current_user_success(self, mock_anon):
        mock_client = MagicMock()
        mock_anon.return_value = mock_client
        mock_user = MagicMock()
        mock_res = MagicMock()
        mock_res.user = mock_user
        mock_client.auth.get_user.return_value = mock_res
        
        user = get_current_user("valid_token")
        self.assertEqual(user, mock_user)
        mock_client.auth.get_user.assert_called_with("valid_token")

    @patch("backend.auth.get_anon_client")
    def test_get_current_user_expired(self, mock_anon):
        mock_client = MagicMock()
        mock_anon.return_value = mock_client
        mock_client.auth.get_user.side_effect = Exception("Expired token")
        
        from fastapi import HTTPException
        with self.assertRaises(HTTPException) as context:
            get_current_user("expired_token")
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Invalid or expired token")

    @patch("backend.auth.get_anon_client")
    def test_refresh_token_success(self, mock_anon):
        mock_client = MagicMock()
        mock_anon.return_value = mock_client
        
        mock_session = MagicMock()
        mock_session.access_token = "new_access"
        mock_session.refresh_token = "new_refresh"
        mock_res = MagicMock()
        mock_res.session = mock_session
        mock_client.auth.refresh_session.return_value = mock_res
        
        access, refresh = refresh_supabase_token("old_refresh")
        self.assertEqual(access, "new_access")
        self.assertEqual(refresh, "new_refresh")
        mock_client.auth.refresh_session.assert_called_with("old_refresh")

    @patch("backend.auth.get_authenticated_client")
    def test_check_rate_limit_new_profile(self, mock_get_auth):
        mock_auth_client = MagicMock()
        mock_get_auth.return_value = mock_auth_client
        
        # Table select returns empty array (no profile yet)
        mock_select_res = MagicMock()
        mock_select_res.data = []
        mock_auth_client.table().select().eq().execute.return_value = mock_select_res
        
        allowed = check_rate_limit("user123", "token123")
        self.assertTrue(allowed)
        
        # Verify insert is called to create profile with count=1
        mock_auth_client.table.assert_called_with("profiles")
        mock_auth_client.table().insert.assert_called()

    @patch("backend.auth.get_authenticated_client")
    def test_check_rate_limit_new_day_reset(self, mock_get_auth):
        mock_auth_client = MagicMock()
        mock_get_auth.return_value = mock_auth_client
        
        # Table select returns last question date as yesterday
        mock_select_res = MagicMock()
        mock_select_res.data = [{"questions_today": 50, "last_question_date": "2020-01-01"}]
        mock_auth_client.table().select().eq().execute.return_value = mock_select_res
        
        allowed = check_rate_limit("user123", "token123")
        self.assertTrue(allowed)
        
        # Verify reset update is called with count=1
        mock_auth_client.table().update.assert_called_with({
            "questions_today": 1,
            "last_question_date": date.today().isoformat(),
        })

    @patch("backend.auth.get_authenticated_client")
    def test_check_rate_limit_under_limit(self, mock_get_auth):
        mock_auth_client = MagicMock()
        mock_get_auth.return_value = mock_auth_client
        
        # Table select returns today's date and count < limit
        mock_select_res = MagicMock()
        mock_select_res.data = [{"questions_today": 5, "last_question_date": date.today().isoformat()}]
        mock_auth_client.table().select().eq().execute.return_value = mock_select_res
        
        allowed = check_rate_limit("user123", "token123")
        self.assertTrue(allowed)
        
        # Verify count is incremented to 6
        mock_auth_client.table().update.assert_called_with({
            "questions_today": 6
        })

    @patch("backend.auth.get_authenticated_client")
    def test_check_rate_limit_exceeded(self, mock_get_auth):
        mock_auth_client = MagicMock()
        mock_get_auth.return_value = mock_auth_client
        
        # Table select returns today's date and count >= limit (100)
        mock_select_res = MagicMock()
        mock_select_res.data = [{"questions_today": 100, "last_question_date": date.today().isoformat()}]
        mock_auth_client.table().select().eq().execute.return_value = mock_select_res
        
        config.DAILY_QUESTION_LIMIT = 100
        allowed = check_rate_limit("user123", "token123")
        self.assertFalse(allowed)
        
        # Verify update is NOT called
        mock_auth_client.table().update.assert_not_called()

    @patch("backend.auth.get_authenticated_client")
    def test_check_rate_limit_fail_open(self, mock_get_auth):
        # Database raises an exception
        mock_get_auth.side_effect = Exception("DB Connection Error")
        
        allowed = check_rate_limit("user123", "token123")
        # Should fail open and return True
        self.assertTrue(allowed)

if __name__ == "__main__":
    unittest.main()

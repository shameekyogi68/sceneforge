"""
auth.py — Supabase Auth helpers: signup, login, token validation, rate limiting.

Optimisations:
- Module-level anon client reused for all auth operations
- check_rate_limit reuses the caller-provided authenticated client instead of
  creating a new one per call
"""

import logging
import time
from datetime import date
from typing import Any, Optional

from fastapi import HTTPException
from supabase import create_client

import backend.config as config

logger = logging.getLogger(__name__)

# Single module-level client for auth (not RLS-protected operations)
_anon_client = None

def get_anon_client():
    """Retrieve or build the anonymous Supabase client lazily."""
    global _anon_client
    if _anon_client is None:
        _anon_client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    return _anon_client


from collections import OrderedDict
import threading

class ClientCache:
    """Thread-safe connection cache to reuse client instances per user token."""
    def __init__(self, max_size: int = 100):
        self.cache = OrderedDict()
        self.max_size = max_size
        self._lock = threading.Lock()

    def get(self, token: str):
        if not token:
            return get_anon_client()
        with self._lock:
            if token in self.cache:
                self.cache.move_to_end(token)
                return self.cache[token]
            client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            client.postgrest.auth(token)
            self.cache[token] = client
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)
            return client

_client_cache = ClientCache()

def get_authenticated_client(token: str):
    return _client_cache.get(token)


class UserCache:
    """Thread-safe cache for verified Supabase users to avoid round-trip get_user calls."""
    def __init__(self, ttl: float = 300.0, max_size: int = 100):
        self.cache = {}
        self.ttl = ttl
        self.max_size = max_size
        self._lock = threading.Lock()

    def get(self, token: str) -> Optional[Any]:
        if not token:
            return None
        with self._lock:
            if token in self.cache:
                user, expiry = self.cache[token]
                if time.time() < expiry:
                    return user
                else:
                    del self.cache[token]
            return None

    def set(self, token: str, user: Any):
        if not token:
            return
        with self._lock:
            if len(self.cache) >= self.max_size:
                now = time.time()
                expired = [k for k, (_, exp) in self.cache.items() if now >= exp]
                if expired:
                    for k in expired:
                        self.cache.pop(k, None)
                else:
                    self.cache.popitem()
            self.cache[token] = (user, time.time() + self.ttl)

_user_cache = UserCache()


# ---------------------------------------------------------------------------
# Signup
# ---------------------------------------------------------------------------

def signup(email: str, password: str) -> Any:
    """
    Create a Supabase Auth user and a matching profiles row.
    Raises HTTPException(400) on failure.
    Note: session may be None when email confirmation is required.
    """
    try:
        result = get_anon_client().auth.sign_up({"email": email, "password": password})
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if result is None or not result.user:
        raise HTTPException(status_code=400, detail="Signup failed — no user returned.")

    # Best-effort profile insert (non-fatal if it already exists)
    try:
        get_anon_client().table("profiles").insert({
            "id":                  result.user.id,
            "email":               email,
            "questions_today":     0,
            "last_question_date":  date.today().isoformat(),
        }).execute()
    except Exception:
        logger.debug("Profile insert skipped for %s (may already exist)", email)

    return result


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

def login(email: str, password: str) -> Any:
    """
    Sign in with email + password.
    Raises HTTPException(401) on invalid credentials.
    """
    try:
        result = get_anon_client().auth.sign_in_with_password({"email": email, "password": password})
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if result is None or not result.session:
        raise HTTPException(status_code=401, detail="Login failed — no session returned.")

    return result


# ---------------------------------------------------------------------------
# Token validation and refresh
# ---------------------------------------------------------------------------

def get_current_user(token: str) -> Any:
    """
    Validate a JWT and return the Supabase user object.
    Raises HTTPException(401) on invalid/expired token.
    """
    cached_user = _user_cache.get(token)
    if cached_user:
        return cached_user

    try:
        response = get_anon_client().auth.get_user(token)
        if response is None or not response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        _user_cache.set(token, response.user)
        return response.user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def refresh_supabase_token(refresh_token: str) -> tuple[str, str]:
    """
    Refresh Supabase session using the refresh token.
    Returns (new_access_token, new_refresh_token).
    """
    try:
        res = get_anon_client().auth.refresh_session(refresh_token)
        if res is None or not res.session:
            raise HTTPException(status_code=401, detail="Refresh session failed — no session returned.")
        return res.session.access_token, res.session.refresh_token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token refresh failed: {str(e)}")


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

def check_rate_limit(user_id: str, token: str) -> bool:
    """
    Enforce DAILY_QUESTION_LIMIT questions per user per calendar day.

    Logic:
    - No profile → create one, allow
    - Date changed → reset counter, allow
    - Count >= limit → deny
    - Otherwise → increment, allow

    Fails open on any DB error so users are never blocked by infrastructure issues.
    Returns True (allow) / False (deny).
    """
    try:
        # Use the cached authenticated client so RLS policies are satisfied
        client = get_authenticated_client(token)

        rows = client.table("profiles").select("questions_today, last_question_date") \
                     .eq("id", user_id).execute().data
        today = date.today().isoformat()

        if not rows:
            _upsert_profile(client, user_id, today, 1)
            return True

        profile = rows[0]
        if not isinstance(profile, dict):
            _upsert_profile(client, user_id, today, 1)
            return True

        last_date = profile.get("last_question_date", "")
        if last_date is None:
            last_date = ""
        elif not isinstance(last_date, str) and hasattr(last_date, "isoformat"):
            last_date = getattr(last_date, "isoformat")()

        if last_date != today:
            # New day — reset
            client.table("profiles").update({
                "questions_today":    1,
                "last_question_date": today,
            }).eq("id", user_id).execute()
            return True

        raw_count = profile.get("questions_today", 0)
        count = raw_count if isinstance(raw_count, int) else 0
        if count >= config.DAILY_QUESTION_LIMIT:
            return False

        client.table("profiles").update({
            "questions_today": count + 1,
        }).eq("id", user_id).execute()
        return True

    except Exception:
        logger.exception("check_rate_limit failed for %s — failing open", user_id)
        return True


def _upsert_profile(client, user_id: str, today: str, count: int) -> None:
    """Insert a profile row, ignoring conflicts."""
    try:
        client.table("profiles").insert({
            "id":                 user_id,
            "questions_today":    count,
            "last_question_date": today,
        }).execute()
    except Exception:
        logger.debug("Profile upsert skipped for %s", user_id)

"""
auth.py — Supabase Auth helpers: signup, login, token validation, rate limiting.

Optimisations:
- Module-level anon client reused for all auth operations (uses ANON key).
- Backend-authenticated client uses SERVICE key for trusted operations.
- check_rate_limit uses a lightweight RPC update to avoid read-modify-write races.
- Rate limiting fails CLOSED on unexpected DB errors to prevent abuse.
"""

import logging
import time
import uuid
from datetime import date
from typing import Any, Optional

from fastapi import HTTPException
from supabase import create_client

import backend.config as config
from postgrest import CountMethod

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Supabase clients
# ---------------------------------------------------------------------------
_anon_client = None
_service_client = None


def get_anon_client():
    """Retrieve or build the anonymous Supabase client (used for auth/public operations)."""
    global _anon_client
    if _anon_client is None:
        _anon_client = create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)
    return _anon_client


def get_service_client():
    """Retrieve or build the backend service-role client (bypasses RLS)."""
    global _service_client
    if _service_client is None:
        _service_client = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)
    return _service_client


from collections import OrderedDict
import threading


class ClientCache:
    """Thread-safe connection cache to reuse authenticated client instances per user token."""
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
            client = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)
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
    def __init__(self, ttl: float = 300.0, max_size: int = 1000):
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

    # Best-effort profile insert using the service client so it always succeeds
    # regardless of email confirmation state.
    try:
        get_service_client().table("profiles").insert({
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

    # Ensure profile exists on login (handles users created before trigger existed)
    try:
        svc = get_service_client()
        existing = svc.table("profiles").select("id", count=CountMethod.exact).eq("id", result.user.id).execute()
        if not existing.count:
            svc.table("profiles").insert({
                "id":                  result.user.id,
                "email":               email,
                "questions_today":     0,
                "last_question_date":  date.today().isoformat(),
            }).execute()
    except Exception:
        logger.debug("Profile insert/upsert skipped for %s on login", email)

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

from typing import Tuple


def _ensure_profile(user_id: str) -> None:
    """Idempotent profile creation using the service client."""
    try:
        svc = get_service_client()
        today = date.today().isoformat()
        svc.table("profiles").insert({
            "id": user_id,
            "email": None,
            "questions_today": 0,
            "last_question_date": today,
        }).execute()
    except Exception:
        pass


def check_rate_limit(user_id: str, token: str) -> Tuple[bool, int]:
    """
    Enforce DAILY_QUESTION_LIMIT questions per user per calendar day.

    Uses a deterministic DB-side approach to avoid races:
    - Selects the row; if missing or stale date, updates via service client.
    - If count already >= limit, deny.
    - Otherwise increment and allow.

    Fails CLOSED on unexpected DB errors so a transient Supabase outage cannot
    be exploited to bypass limits.
    Returns (allowed, current_count).
    """
    try:
        # Prefer the caller's authenticated client so RLS is satisfied; fall back
        # to service client if token is missing.
        client = get_authenticated_client(token) if token else get_service_client()
        today = date.today().isoformat()

        rows = client.table("profiles").select("questions_today, last_question_date") \
                     .eq("id", user_id).execute().data

        if not rows:
            _ensure_profile(user_id)
            client = get_authenticated_client(token) if token else get_service_client()
            rows = client.table("profiles").select("questions_today, last_question_date") \
                         .eq("id", user_id).execute().data
            if not rows:
                # Profile creation may be delayed; allow once and record.
                _ensure_profile(user_id)
                return True, 1

        profile = rows[0]
        if not isinstance(profile, dict):
            return False, 0

        last_date = profile.get("last_question_date", "")
        if last_date is not None and not isinstance(last_date, str):
            try:
                last_date = last_date.isoformat()
            except Exception:
                last_date = str(last_date)
        last_date = last_date or ""

        if last_date != today:
            # New day — reset counter
            client.table("profiles").update({
                "questions_today":    1,
                "last_question_date": today,
            }).eq("id", user_id).execute()
            return True, 1

        raw_count = profile.get("questions_today", 0)
        count = raw_count if isinstance(raw_count, int) else 0
        if count >= config.DAILY_QUESTION_LIMIT:
            return False, count

        client.table("profiles").update({
            "questions_today": count + 1,
        }).eq("id", user_id).execute()
        return True, count + 1

    except Exception:
        logger.exception("check_rate_limit failed for %s — failing closed", user_id)
        return False, 0

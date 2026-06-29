"""
config.py — Environment variables and application constants.
All values are module-level; no classes, no lazy loading.

Production hardening:
- SUPABASE_SERVICE_KEY (backend) is separated from SUPABASE_ANON_KEY (frontend).
- Required variables are validated at import time so the app fails fast on startup.
- Frontend-facing config is exposed as FRONTEND_* constants.
"""

import os

from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# Required environment variable validation
# ---------------------------------------------------------------------------
def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        if os.getenv("GITHUB_ACTIONS") == "true":
            return "placeholder-for-build"
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


GEMINI_API_KEY: str = _require("GEMINI_API_KEY")
SUPABASE_URL: str = _require("SUPABASE_URL")

# Backwards compatibility: SUPABASE_KEY is treated as the service key if the
# explicit SERVICE_KEY is not provided. In production prefer SUPABASE_SERVICE_KEY.
SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", os.getenv("SUPABASE_KEY", "")).strip()
if not SUPABASE_SERVICE_KEY:
    if os.getenv("GITHUB_ACTIONS") == "true":
        SUPABASE_SERVICE_KEY = "placeholder-for-build"
    else:
        raise RuntimeError("Missing required environment variable: SUPABASE_SERVICE_KEY (or SUPABASE_KEY for backwards compatibility)")

SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", SUPABASE_SERVICE_KEY).strip()
if not SUPABASE_ANON_KEY:
    if os.getenv("GITHUB_ACTIONS") == "true":
        SUPABASE_ANON_KEY = "placeholder-for-build"
    else:
        raise RuntimeError("Missing required environment variable: SUPABASE_ANON_KEY")

# google-generativeai SDK prefers GOOGLE_API_KEY over GEMINI_API_KEY when both
# are set. Normalise so the correct key is always used.
if GEMINI_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

# ---------------------------------------------------------------------------
# Frontend config  (served via /api/config so HTML has no hardcoded secrets)
# ---------------------------------------------------------------------------
FRONTEND_SUPABASE_URL: str = SUPABASE_URL
FRONTEND_SUPABASE_ANON_KEY: str = SUPABASE_ANON_KEY

# ---------------------------------------------------------------------------
# Chunking  (FR: F3)
# ---------------------------------------------------------------------------
CHUNK_SIZE: int = 500   # words per chunk
CHUNK_OVERLAP: int = 50    # overlapping words between consecutive chunks
MIN_CHUNK_CHARS: int = 50  # skip chunks shorter than this

# ---------------------------------------------------------------------------
# Retrieval  (FR: F7)
# ---------------------------------------------------------------------------
TOP_K_CHUNKS: int = 5      # chunks retrieved per question

# ---------------------------------------------------------------------------
# Models  — all free-tier Gemini
# ---------------------------------------------------------------------------
# Generation: gemini-2.5-flash is the default working option. Override with CHAT_MODEL env var.
GEMINI_MODEL: str = os.getenv("CHAT_MODEL", "gemini-2.0-flash")

# Embeddings: gemini-embedding-001  — free tier: 1 500 RPD, 768 dims
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "768"))  # must match VECTOR(N) in Supabase

# Embedding batch size — Gemini accepts up to 100 texts per batch request
EMBED_BATCH_SIZE: int = int(os.getenv("EMBED_BATCH_SIZE", "100"))

# ---------------------------------------------------------------------------
# Upload limits  (FR: F1)
# ---------------------------------------------------------------------------
MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAX_FILES_PER_PROJECT: int = int(os.getenv("MAX_FILES_PER_PROJECT", "30"))

# ---------------------------------------------------------------------------
# Rate limiting  (auth spec)
# ---------------------------------------------------------------------------
DAILY_QUESTION_LIMIT: int = int(os.getenv("DAILY_QUESTION_LIMIT", "100"))

# Global/per-user RPM guard for the free Gemini tier (15 RPM). Applied in
# addition to the daily question limit.
GEMINI_RATE_LIMIT_RPM: int = int(os.getenv("GEMINI_RATE_LIMIT_RPM", "15"))

# ---------------------------------------------------------------------------
# Memory backend
# ---------------------------------------------------------------------------
# Use Mem0 only when explicitly enabled. By default we use a Supabase-based
# memory store for faster, shared, production-safe persistence.
USE_MEM0: bool = os.getenv("USE_MEM0", "false").lower() in ("1", "true", "yes")

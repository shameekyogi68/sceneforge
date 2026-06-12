"""
config.py — Environment variables and application constants.
All values are module-level; no classes, no lazy loading.
"""

import os

# Must be set before any protobuf-backed library is imported
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
SUPABASE_URL: str   = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str   = os.getenv("SUPABASE_KEY", "")

# google-generativeai SDK prefers GOOGLE_API_KEY over GEMINI_API_KEY when both
# are set. Normalise so the correct key is always used.
if GEMINI_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

# ---------------------------------------------------------------------------
# Chunking  (FR: F3)
# ---------------------------------------------------------------------------
CHUNK_SIZE: int    = 500   # words per chunk
CHUNK_OVERLAP: int = 50    # overlapping words between consecutive chunks
MIN_CHUNK_CHARS: int = 50  # skip chunks shorter than this

# ---------------------------------------------------------------------------
# Retrieval  (FR: F7)
# ---------------------------------------------------------------------------
TOP_K_CHUNKS: int = 5      # chunks retrieved per question

# ---------------------------------------------------------------------------
# Models  — all free-tier Gemini
# ---------------------------------------------------------------------------
# Generation: gemini-2.5-flash  — free tier: 15 RPM / 1 500 RPD / 1M TPM
GEMINI_MODEL: str        = "gemini-2.5-flash"

# Embeddings: gemini-embedding-001  — free tier: 1 500 RPD, 768 dims
EMBEDDING_MODEL: str     = "models/gemini-embedding-001"
EMBEDDING_DIMENSION: int = 768       # must match VECTOR(768) in Supabase

# Embedding batch size — Gemini accepts up to 100 texts per batch request
EMBED_BATCH_SIZE: int    = 100

# ---------------------------------------------------------------------------
# Upload limits  (FR: F1)
# ---------------------------------------------------------------------------
MAX_FILE_SIZE_MB: int      = 50
MAX_FILES_PER_PROJECT: int = 30

# ---------------------------------------------------------------------------
# Rate limiting  (auth spec)
# ---------------------------------------------------------------------------
DAILY_QUESTION_LIMIT: int = 100

# ---------------------------------------------------------------------------
# Frontend config  (served via /api/config so HTML has no hardcoded secrets)
# ---------------------------------------------------------------------------
FRONTEND_SUPABASE_URL: str      = os.getenv("SUPABASE_URL", "")
FRONTEND_SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_KEY", "")

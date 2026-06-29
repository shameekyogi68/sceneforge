"""
memory.py — Mem0 cross-session project memory using Gemini (100 % free).
All public functions are silent — they never raise.
"""

import logging
from typing import Dict, List, cast, Any

import backend.config as config

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Mem0 initialisation
# ---------------------------------------------------------------------------

class _NoopMemory:
    """Drop-in no-op used when Mem0 cannot be initialised."""
    def add(self, *a, **kw):        raise RuntimeError("Mem0 not available")
    def get_all(self, *a, **kw):    raise RuntimeError("Mem0 not available")
    def delete_all(self, *a, **kw): raise RuntimeError("Mem0 not available")


def _build_memory():
    """
    Build a Mem0 Memory client using Gemini for both LLM and embeddings.
    Falls back to _NoopMemory if anything fails (app still works, just no memory).
    """
    try:
        from mem0 import Memory
        cfg = {
            "llm": {
                "provider": "gemini",
                "config": {
                    "model":       config.GEMINI_MODEL,   # gemini-2.5-flash — free
                    "temperature": 0.1,
                    "max_tokens":  512,                   # memory extracts are short
                },
            },
            "embedder": {
                "provider": "gemini",
                "config": {
                    "model":          "models/text-embedding-004",  # free, 768 dims
                    "embedding_dims": 768,
                },
            },
            "vector_store": {
                "provider": "qdrant",
                "config": {"path": "./mem0"},             # local file storage
            },
        }
        return Memory.from_config(cfg)
    except Exception:
        logger.warning(
            "Mem0 could not be initialised — cross-session memory disabled. "
            "All other features work normally."
        )
        return _NoopMemory()


_memory = None


def _get_memory():
    """Retrieve or build the Mem0 client lazily."""
    global _memory
    if _memory is None:
        if config.USE_MEM0:
            _memory = _build_memory()
        else:
            _memory = _NoopMemory()
    return _memory


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def save_conversation_memory(messages: List[Dict], user_id: str) -> None:
    """Persist a conversation exchange. Silently ignores all errors."""
    try:
        _get_memory().add(messages, user_id=user_id)
    except Exception:
        logger.debug("save_conversation_memory skipped for %s", user_id)


def get_project_memory(user_id: str) -> str:
    """
    Return stored memories as a bullet list, or "" on empty / error.
    Returns at most 10 memory items to keep the prompt concise.
    """
    try:
        result = _get_memory().get_all(user_id=user_id)
        if not result:
            return ""

        mem_data = result if isinstance(result, list) else (result.get("results", []) if isinstance(result, dict) else [])
        memories = cast(List[Any], mem_data)
        if not memories:
            return ""

        items = []
        for mem in memories[:10]:
            text = (mem.get("memory") or mem.get("text") or str(mem)) \
                   if isinstance(mem, dict) else str(mem)
            items.append(f"• {text}")

        return "Relevant facts from previous sessions:\n" + "\n".join(items) \
               if items else ""

    except Exception:
        logger.debug("get_project_memory skipped for %s", user_id)
        return ""


def clear_project_memory(user_id: str) -> None:
    """Delete all memories for a project. Silently ignores all errors."""
    try:
        _get_memory().delete_all(user_id=user_id)
    except Exception:
        logger.debug("clear_project_memory skipped for %s", user_id)

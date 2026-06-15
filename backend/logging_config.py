import logging
import os
import sys

def setup_logging():
    """Configure structured logging for SceneForge."""
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    # Simple clean format for local console, but fully structured
    log_format = (
        "[%(asctime)s] %(levelname)s in %(name)s (%(filename)s:%(lineno)d): "
        "%(message)s"
    )

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Lower third-party log noisiness
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("supabase").setLevel(logging.WARNING)
    logging.getLogger("gotrue").setLevel(logging.WARNING)
    logging.getLogger("postgrest").setLevel(logging.WARNING)
    logging.getLogger("reflex").setLevel(logging.INFO)

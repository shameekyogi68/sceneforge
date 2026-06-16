import os
import reflex as rx
from reflex.plugins import RadixThemesPlugin
from reflex_base.plugins.sitemap import SitemapPlugin

# In production (Reflex Cloud), API_URL must point to the same origin as the
# app so the frontend build bakes the correct WebSocket host into env.json.
# A wrong or missing value here causes the browser to connect to a dead host
# and receive a 403.
api_url = os.getenv("API_URL", "https://sceneforge-aqua-ocean.reflex.run")

config = rx.Config(
    app_name="sceneforge",
    api_url=api_url,
    cors_allowed_origins=[
        origin.strip() for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if origin.strip()
    ] or [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://sceneforge-aqua-ocean.reflex.run",
    ],
    plugins=[RadixThemesPlugin(), SitemapPlugin()],
)

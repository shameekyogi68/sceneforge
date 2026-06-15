import os
import reflex as rx

api_url = os.getenv("API_URL", "http://localhost:8000")

config = rx.Config(
    app_name="sceneforge",
    api_url=api_url,
    cors_allowed_origins=[
        origin.strip() for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if origin.strip()
    ] or [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    state_auto_setters=True,
    plugins=[
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                appearance="dark",
                has_background=True,
                accent_color="indigo",
            )
        )
    ],
)

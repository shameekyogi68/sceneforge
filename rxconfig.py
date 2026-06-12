import os
import reflex as rx

api_url = os.getenv("API_URL", "http://localhost:8000")

config = rx.Config(
    app_name="sceneforge",
    api_url=api_url,
    cors_allowed_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://sceneforge-lime-wood.reflex.run",
        "https://00152787-d926-49c9-910f-975d1eae00ca.fly.dev",
        "https://sceneforge-aqua-ocean.reflex.run",
        "https://b2d09cec-8f73-4370-b726-2907b4163a38.fly.dev",
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

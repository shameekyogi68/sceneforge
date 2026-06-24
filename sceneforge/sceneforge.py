import reflex as rx
from sceneforge.pages.login import login_page
from sceneforge.pages.dashboard import dashboard_page
from sceneforge.pages.project import project_page
from sceneforge.pages.callback import callback_page
from sceneforge.pages.legal import terms_page, privacy_page
from sceneforge.state import State, AuthState

from sceneforge.styles import GLOBAL_CSS

from backend.main import app as fastapi_app

from reflex_components_core.core import banner
banner.connection_toaster = lambda *args, **kwargs: rx.fragment()  # type: ignore
banner.connection_modal = lambda *args, **kwargs: rx.fragment()  # type: ignore
banner.connection_pulser = lambda *args, **kwargs: rx.fragment()  # type: ignore

app = rx.App(
    style={
        "font_family": "'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif",
    },
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap",
    ],
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
    ],
    hydrate_fallback=rx.box(
        rx.center(
            rx.heading(
                "ScriptIQ",
                size="9",
                font_family="'Plus Jakarta Sans', sans-serif",
                font_weight="800",
                letter_spacing="-0.02em",
                color="#00F0FF",
                style={
                    "text_shadow": "0 0 15px rgba(0, 240, 255, 0.4)",
                }
            ),
            width="100vw",
            height="100vh",
            background_color="#05080F",
        )
    ),
    api_transformer=fastapi_app,
)

import logging
logger = logging.getLogger("sceneforge")
logger.info("Configured CORS Allowed Origins: %s", rx.config.get_config().cors_allowed_origins)
logger.info("Configured API URL: %s", rx.config.get_config().api_url)

from typing import Any, cast

# Register pages
app.add_page(login_page, route="/login", on_load=cast(Any, State.check_auth_login))
app.add_page(dashboard_page, route="/dashboard", on_load=cast(Any, State.check_auth))
app.add_page(project_page, route="/project")
app.add_page(callback_page, route="/auth/v1/callback")
app.add_page(terms_page, route="/terms")
app.add_page(privacy_page, route="/privacy")


# Index page redirects dynamically based on session status
@rx.page(route="/", on_load=cast(Any, State.check_auth_index))
def index():
    return rx.center(
        rx.html(f"<style>{GLOBAL_CSS}</style>"),
        rx.vstack(
            rx.heading(
                "ScriptIQ",
                size="8",
                font_weight="800",
                font_family="'Plus Jakarta Sans', sans-serif",
                letter_spacing="-0.04em",
                style={
                    "background": "linear-gradient(135deg, #c7d2fe 0%, #a5b4fc 40%, #c084fc 100%)",
                    "-webkit-background-clip": "text",
                    "-webkit-text-fill-color": "transparent",
                    "background-clip": "text",
                },
            ),
            rx.html("""
                <div style="
                    width: 20px; height: 20px;
                    border: 2px solid rgba(99,102,241,0.2);
                    border-top-color: #818cf8;
                    border-radius: 50%;
                    animation: spin-slow 0.8s linear infinite;
                "></div>
            """),
            align="center",
            spacing="4",
        ),
        height="100vh",
        background_color="transparent",
        width="100%",
    )

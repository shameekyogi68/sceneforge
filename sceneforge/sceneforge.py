import reflex as rx
from sceneforge.pages.login import login_page
from sceneforge.pages.dashboard import dashboard_page
from sceneforge.pages.project import project_page
from sceneforge.pages.callback import callback_page
from sceneforge.pages.legal import terms_page, privacy_page
from sceneforge.state import State, AuthState, ProjectState

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
                font_family="'Courier Prime', 'Courier New', Courier, monospace",
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
app.add_page(project_page, route="/project", on_load=cast(Any, ProjectState.on_load_project))
app.add_page(callback_page, route="/auth/v1/callback")
app.add_page(terms_page, route="/terms")
app.add_page(privacy_page, route="/privacy")


# Index page redirects dynamically based on session status
@rx.page(route="/", on_load=cast(Any, State.check_auth_index))
def index():
    from sceneforge.pages.navigation import app_icon
    from sceneforge.pages.dashboard import project_skeleton_card
    
    return rx.box(
        rx.html(f"<style>{GLOBAL_CSS}</style>"),
        rx.hstack(
            # Skeleton Sidebar
            rx.vstack(
                rx.center(
                    app_icon(size="42px", icon_size="18px"),
                    padding_y="28px",
                    width="100%",
                ),
                rx.vstack(
                    rx.box(width="40px", height="40px", border_radius="10px", background="rgba(255,255,255,0.03)", style={"animation": "statusPulse 1.5s infinite"}),
                    rx.box(width="40px", height="40px", border_radius="10px", background="rgba(255,255,255,0.03)", style={"animation": "statusPulse 1.5s infinite 0.25s"}),
                    spacing="4",
                    width="100%",
                    align_items="center",
                ),
                rx.spacer(),
                rx.box(width="34px", height="34px", border_radius="50%", background="rgba(255,255,255,0.03)", style={"animation": "statusPulse 1.5s infinite 0.5s"}),
                width="68px",
                height="100vh",
                background="rgba(4, 6, 12, 0.95)",
                border_right="1px solid rgba(255, 255, 255, 0.05)",
                align_items="center",
                flex_shrink="0",
                padding_bottom="16px",
            ),
            # Main Content Skeleton
            rx.vstack(
                # Top header skeleton
                rx.hstack(
                    rx.box(width="240px", height="32px", background="rgba(255,255,255,0.03)", border_radius="4px", style={"animation": "statusPulse 1.5s infinite"}),
                    rx.spacer(),
                    rx.box(width="260px", height="40px", background="rgba(255,255,255,0.02)", border_radius="20px", style={"animation": "statusPulse 1.5s infinite"}),
                    rx.box(width="120px", height="40px", background="rgba(255,255,255,0.02)", border_radius="20px", style={"animation": "statusPulse 1.5s infinite 0.25s"}),
                    rx.box(width="120px", height="40px", background="rgba(255,255,255,0.02)", border_radius="20px", style={"animation": "statusPulse 1.5s infinite 0.5s"}),
                    width="100%",
                    align_items="center",
                    spacing="4",
                    padding_bottom="12px",
                ),
                rx.box(width="100%", height="1px", background="rgba(255,255,255,0.06)", margin_y="4px"),
                # Section title skeleton
                rx.box(width="200px", height="24px", background="rgba(255,255,255,0.03)", border_radius="4px", style={"animation": "statusPulse 1.5s infinite 0.25s"}, margin_top="16px"),
                rx.box(width="380px", height="14px", background="rgba(255,255,255,0.02)", border_radius="4px", style={"animation": "statusPulse 1.5s infinite 0.4s"}),
                # Skeleton grid
                rx.grid(
                    project_skeleton_card(), project_skeleton_card(), project_skeleton_card(),
                    columns=rx.breakpoints(initial="1", sm="2", md="3"), spacing="5", width="100%",
                    margin_top="24px",
                ),
                width="100%",
                height="100vh",
                padding="40px",
                spacing="6",
                overflow="hidden",
            ),
            width="100%",
            height="100vh",
            align_items="start",
            spacing="0",
        ),
        background_color="#05080F",
        width="100vw",
        height="100vh",
        overflow="hidden",
    )

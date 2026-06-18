import reflex as rx
from sceneforge.pages.login import login_page
from sceneforge.pages.dashboard import dashboard_page
from sceneforge.pages.project import project_page
from sceneforge.pages.callback import callback_page
from sceneforge.pages.legal import terms_page, privacy_page
from sceneforge.state import State, AuthState

from sceneforge.styles import GLOBAL_CSS

from backend.main import app as fastapi_app

app = rx.App(
    style={
        "font_family": "'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif",
    },
    stylesheets=[
        # Inlined via a data URI approach — we inject via html component in each page
    ],
    api_transformer=fastapi_app,
)

# Inject global CSS into every page via the app's head
# (Reflex 0.9.x: use add_page + inject html style tag in root component)

from typing import Any, cast

# Register pages
app.add_page(login_page, route="/login", on_load=cast(Any, State.check_auth_login))
app.add_page(dashboard_page, route="/dashboard", on_load=cast(Any, State.check_auth))
app.add_page(project_page, route="/project")
app.add_page(callback_page, route="/auth/v1/callback", on_load=cast(Any, AuthState.handle_callback_load))
app.add_page(terms_page, route="/terms")
app.add_page(privacy_page, route="/privacy")


# Index page redirects dynamically based on session status
@rx.page(route="/", on_load=cast(Any, State.check_auth_index))
def index():
    return rx.center(
        rx.html(f"<style>{GLOBAL_CSS}</style>"),
        rx.html("""
            <div style="display:flex;flex-direction:column;align-items:center;gap:16px;">
                <div style="
                    width:48px;height:48px;
                    background:linear-gradient(135deg,rgba(99,102,241,0.15),rgba(168,85,247,0.12));
                    border:1px solid rgba(99,102,241,0.3);
                    border-radius:14px;
                    display:flex;align-items:center;justify-content:center;
                ">
                    <svg style="width:22px;height:22px;color:#a5b4fc;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20.2 6 3 11l-.9-2.4 17.2-5.1Z"/>
                        <path d="M2 12V4a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-4"/>
                        <path d="M2 12h20"/>
                        <path d="m7 2 2 4"/><path d="m12 2 2 4"/><path d="m17 2 2 4"/>
                    </svg>
                </div>
                <div style="width:20px;height:20px;border:2px solid rgba(99,102,241,0.2);border-top-color:#818cf8;border-radius:50%;animation:spin-slow 0.8s linear infinite;"></div>
            </div>
        """),
        height="100vh",
        background_color="#080810",
        width="100%",
    )

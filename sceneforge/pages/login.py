import reflex as rx
from typing import Any, cast
from sceneforge.state import AuthState
from sceneforge.styles import GLOBAL_CSS, SCREENPLAY_FONT_FAMILY
from sceneforge.pages.navigation import app_icon

body_style = {
    "font_family": "'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif",
    "background_color": "#05080F",
    "min_height": "100vh",
    "color": "#f4f4f5",
    "position": "relative",
    "overflow": "hidden",
    "display": "flex",
    "align_items": "center",
    "justify_content": "center",
}

KEYFRAMES = """
@keyframes floatOrb {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33%       { transform: translate(30px, -40px) scale(1.05); }
  66%       { transform: translate(-20px, 20px) scale(0.97); }
}
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(32px); }
  to   { opacity: 1; transform: translateY(0); }
}
"""

def ambient_orbs() -> rx.Component:
    """Animated multi-layered ambient background orbs."""
    return rx.fragment(
        rx.box(
            width="600px", height="600px",
            background="radial-gradient(circle at center, rgba(0,240,255,0.08) 0%, transparent 70%)",
            position="absolute", border_radius="50%", filter="blur(80px)",
            top="-20%", left="-10%", z_index="0", pointer_events="none",
            style={"animation": "floatOrb 18s ease-in-out infinite"},
        ),
        rx.box(
            width="700px", height="700px",
            background="radial-gradient(circle at center, rgba(0,180,255,0.06) 0%, transparent 70%)",
            position="absolute", border_radius="50%", filter="blur(90px)",
            bottom="-20%", right="-10%", z_index="0", pointer_events="none",
            style={"animation": "floatOrb 22s ease-in-out infinite reverse"},
        ),
    )

def google_icon() -> rx.Component:
    return rx.html(
        """<svg style="width:18px; height:18px; flex-shrink:0;" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
            <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
            <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
            <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
            <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
            <path fill="none" d="M0 0h48v48H0z"/>
        </svg>"""
    )

def login_page() -> rx.Component:
    return rx.box(
        rx.html(f"<style>{GLOBAL_CSS}{KEYFRAMES}</style>"),
        ambient_orbs(),
        
        # Card
        rx.vstack(
            # App icon container matching mockup
            rx.center(
                app_icon(size="64px", icon_size="28px"),
                margin_bottom="12px",
            ),
            
            rx.vstack(
                rx.text(
                    "AI Screenplay Writing Assistant powered by Research",
                    color="rgba(255,255,255,0.65)",
                    font_size="0.82rem",
                    text_align="center",
                    letter_spacing="0.04em",
                    font_family=SCREENPLAY_FONT_FAMILY,
                ),
                align="center",
                spacing="2",
                style={"animation": "fadeSlideUp 0.6s cubic-bezier(0.16,1,0.3,1) 0.1s both"},
            ),

            # ── Decorative Divider ────────────────────────────────────
            rx.box(
                rx.hstack(
                    rx.box(height="1px", width="100%", background="linear-gradient(90deg, transparent, rgba(0,240,255,0.15))"),
                    rx.text("SECURE WRITER ACCESS", class_name="hud-text", font_size="0.6rem", color="rgba(0,240,255,0.5)", white_space="nowrap"),
                    rx.box(height="1px", width="100%", background="linear-gradient(-90deg, transparent, rgba(0,240,255,0.15))"),
                    spacing="3",
                    align_items="center",
                    width="100%",
                ),
                margin_top="36px",
                margin_bottom="12px",
                width="100%",
            ),

            # ── Google CTA ────────────────────────────────────────────
            rx.box(
                rx.button(
                    google_icon(),
                    rx.text("Continue with Google", font_size="0.95rem", font_weight="700", letter_spacing="0.01em"),
                    background="rgba(0, 240, 255, 0.05)",
                    color="#E2E8F0",
                    border="1px solid rgba(0, 240, 255, 0.25)",
                    border_radius="100px",  # Rounded button pill matching mock
                    width="100%",
                    padding_y="22px",
                    cursor="pointer",
                    gap="12px",
                    box_shadow="0 0 15px rgba(0, 240, 255, 0.15)",
                    transition="all 0.2s cubic-bezier(0.16, 1, 0.3, 1)",
                    _hover={
                        "box_shadow": "0 0 25px rgba(0, 240, 255, 0.45)",
                        "background": "rgba(0, 240, 255, 0.12)",
                        "border_color": "#00F0FF",
                        "transform": "translateY(-1px)",
                    },
                    _active={"transform": "scale(0.98)"},
                    on_click=cast(Any, AuthState.login_with_google),
                ),
                width="100%",
                margin_top="12px",
            ),
            
            # ── Footer ────────────────────────────────────────────────
            rx.box(
                rx.hstack(
                    rx.text("By signing in you agree to ScriptIQ's ", color="rgba(255,255,255,0.45)", font_size="0.72rem"),
                    rx.link("Terms", href="/terms", color="#00F0FF", font_size="0.72rem", text_decoration="none", _hover={"text_shadow": "0 0 8px rgba(0,240,255,0.5)"}),
                    rx.text(" & ", color="rgba(255,255,255,0.45)", font_size="0.72rem"),
                    rx.link("Privacy Policy", href="/privacy", color="#00F0FF", font_size="0.72rem", text_decoration="none", _hover={"text_shadow": "0 0 8px rgba(0,240,255,0.5)"}),
                    spacing="1",
                    justify="center",
                    wrap="wrap",
                    margin_top="28px",
                ),
                width="100%",
                style={"animation": "fadeSlideUp 0.6s cubic-bezier(0.16,1,0.3,1) 0.55s both"},
            ),

            class_name="glass-panel-glow page-transition",
            width="100%",
            max_width="430px",
            border_radius="24px",
            padding="48px 36px",
            z_index="1",
            style={
                "animation": "fadeSlideUp 0.7s cubic-bezier(0.16,1,0.3,1) both",
                "box_shadow": "0 20px 50px rgba(0,0,0,0.7), 0 0 40px rgba(0, 240, 255, 0.07)",
            },
        ),
        style=body_style,
    )

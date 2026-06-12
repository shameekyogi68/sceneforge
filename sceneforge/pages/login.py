import reflex as rx
from sceneforge.state import AuthState
from sceneforge.styles import GLOBAL_CSS

body_style = {
    "font_family": "'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif",
    "background_color": "#080810",
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
@keyframes floatOrb2 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  40%       { transform: translate(-40px, 30px) scale(1.08); }
  70%       { transform: translate(20px, -20px) scale(0.95); }
}
@keyframes floatOrb3 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50%       { transform: translate(25px, 35px) scale(1.04); }
}
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(32px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
@keyframes shimmer {
  0%   { background-position: -200% center; }
  100% { background-position:  200% center; }
}
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.15); }
  50%       { box-shadow: 0 0 40px rgba(99, 102, 241, 0.35), 0 0 80px rgba(168, 85, 247, 0.15); }
}
@keyframes spin-slow {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
@keyframes logoEntrance {
  0%   { opacity: 0; transform: scale(0.7) rotate(-10deg); filter: blur(8px); }
  60%  { opacity: 1; transform: scale(1.05) rotate(2deg); filter: blur(0px); }
  100% { opacity: 1; transform: scale(1) rotate(0deg); filter: blur(0px); }
}
@keyframes borderPulse {
  0%, 100% { border-color: rgba(255,255,255,0.08); }
  50%       { border-color: rgba(99,102,241,0.25); }
}
"""


def ambient_orbs() -> rx.Component:
    """Animated multi-layered ambient background orbs."""
    return rx.fragment(
        # Primary indigo orb — top left
        rx.box(
            width="600px",
            height="600px",
            background="radial-gradient(circle at center, rgba(99,102,241,0.55) 0%, rgba(79,70,229,0.25) 45%, transparent 70%)",
            position="absolute",
            border_radius="50%",
            filter="blur(80px)",
            opacity="0.18",
            top="-220px",
            left="-180px",
            z_index="0",
            pointer_events="none",
            style={"animation": "floatOrb 18s ease-in-out infinite"},
        ),
        # Purple orb — bottom right
        rx.box(
            width="700px",
            height="700px",
            background="radial-gradient(circle at center, rgba(168,85,247,0.5) 0%, rgba(124,58,237,0.2) 45%, transparent 70%)",
            position="absolute",
            border_radius="50%",
            filter="blur(90px)",
            opacity="0.16",
            bottom="-280px",
            right="-200px",
            z_index="0",
            pointer_events="none",
            style={"animation": "floatOrb2 22s ease-in-out infinite"},
        ),
        # Subtle cyan accent — mid right
        rx.box(
            width="350px",
            height="350px",
            background="radial-gradient(circle at center, rgba(34,211,238,0.3) 0%, transparent 65%)",
            position="absolute",
            border_radius="50%",
            filter="blur(60px)",
            opacity="0.08",
            top="30%",
            right="-80px",
            z_index="0",
            pointer_events="none",
            style={"animation": "floatOrb3 26s ease-in-out infinite"},
        ),
        # Subtle grid overlay
        rx.box(
            position="absolute",
            top="0", left="0", right="0", bottom="0",
            background_image="linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px)",
            background_size="60px 60px",
            z_index="0",
            pointer_events="none",
        ),
    )


def clapperboard_logo() -> rx.Component:
    return rx.box(
        rx.html(
            """
            <div style="
                width:64px; height:64px;
                background: linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(168,85,247,0.12) 100%);
                border: 1px solid rgba(99,102,241,0.3);
                border-radius: 18px;
                display: flex; align-items: center; justify-content: center;
                box-shadow: 0 0 30px rgba(99,102,241,0.2), inset 0 1px 0 rgba(255,255,255,0.08);
                animation: logoEntrance 0.8s cubic-bezier(0.34,1.56,0.64,1) both, pulse-glow 4s ease-in-out infinite 1s;
            ">
                <svg style="width:30px; height:30px; color: #a5b4fc;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20.2 6 3 11l-.9-2.4 17.2-5.1Z"/>
                    <path d="M2 12V4a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-4"/>
                    <path d="M2 12h20"/>
                    <path d="m7 2 2 4"/><path d="m12 2 2 4"/><path d="m17 2 2 4"/>
                </svg>
            </div>
            """
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

            # ── Logo + wordmark ──────────────────────────────────────
            rx.vstack(
                clapperboard_logo(),
                rx.box(
                    rx.heading(
                        "SceneForge",
                        size="8",
                        font_weight="800",
                        letter_spacing="-0.04em",
                        style={
                            "background": "linear-gradient(135deg, #c7d2fe 0%, #a5b4fc 40%, #c084fc 100%)",
                            "background_size": "200% auto",
                            "-webkit-background-clip": "text",
                            "-webkit-text-fill-color": "transparent",
                            "background-clip": "text",
                            "animation": "shimmer 4s linear infinite",
                        },
                    ),
                    margin_top="18px",
                ),
                rx.text(
                    "Film research, powered by AI",
                    color="rgba(161,161,170,0.85)",
                    font_size="0.92rem",
                    text_align="center",
                    letter_spacing="0.01em",
                ),
                rx.text(
                    "Upload PDFs · Ask anything · Get sourced answers",
                    color="rgba(113,113,122,0.7)",
                    font_size="0.78rem",
                    text_align="center",
                    letter_spacing="0.02em",
                ),
                align="center",
                spacing="2",
                style={"animation": "fadeSlideUp 0.6s cubic-bezier(0.16,1,0.3,1) 0.1s both"},
            ),

            # ── Divider ───────────────────────────────────────────────
            rx.box(
                height="1px",
                width="100%",
                background="linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.1) 30%, rgba(99,102,241,0.3) 50%, rgba(255,255,255,0.1) 70%, transparent 100%)",
                margin_y="28px",
                style={"animation": "fadeIn 0.5s ease 0.4s both"},
            ),

            # ── Google CTA ────────────────────────────────────────────
            rx.box(
                rx.button(
                    google_icon(),
                    rx.text("Continue with Google", font_size="0.96rem", font_weight="600", letter_spacing="0.01em"),
                    background="rgba(255,255,255,0.04)",
                    color="#f4f4f5",
                    border="1px solid rgba(255,255,255,0.1)",
                    border_radius="14px",
                    width="100%",
                    padding_y="20px",
                    cursor="pointer",
                    gap="10px",
                    transition="all 0.25s cubic-bezier(0.16,1,0.3,1)",
                    _hover={
                        "background": "rgba(255,255,255,0.08)",
                        "border_color": "rgba(99,102,241,0.5)",
                        "box_shadow": "0 8px 32px rgba(99,102,241,0.18), 0 0 0 1px rgba(99,102,241,0.15)",
                        "transform": "translateY(-1px)",
                    },
                    _active={"transform": "translateY(1px)", "box_shadow": "none"},
                    on_click=AuthState.login_with_google,
                    style={"position": "relative", "overflow": "hidden"},
                ),
                width="100%",
                style={"animation": "fadeSlideUp 0.6s cubic-bezier(0.16,1,0.3,1) 0.3s both"},
            ),

            # ── Feature badges ────────────────────────────────────────
            rx.hstack(
                rx.box(
                    rx.html("""<div style="display:flex;align-items:center;gap:6px;font-size:0.72rem;color:rgba(161,161,170,0.7);font-weight:500;">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="rgba(52,211,153,0.8)" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>
                        Source citations
                    </div>"""),
                ),
                rx.box(
                    rx.html("""<div style="display:flex;align-items:center;gap:6px;font-size:0.72rem;color:rgba(161,161,170,0.7);font-weight:500;">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="rgba(52,211,153,0.8)" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>
                        Zero hallucination
                    </div>"""),
                ),
                rx.box(
                    rx.html("""<div style="display:flex;align-items:center;gap:6px;font-size:0.72rem;color:rgba(161,161,170,0.7);font-weight:500;">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="rgba(52,211,153,0.8)" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>
                        Free to use
                    </div>"""),
                ),
                spacing="4",
                justify="center",
                wrap="wrap",
                style={"animation": "fadeSlideUp 0.6s cubic-bezier(0.16,1,0.3,1) 0.45s both"},
            ),

            # ── Error / Success alerts ────────────────────────────────
            rx.cond(
                AuthState.error_message != "",
                rx.box(
                    rx.hstack(
                        rx.html("""<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f87171" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>"""),
                        rx.text(AuthState.error_message, color="#fca5a5", font_size="0.86rem", line_height="1.5"),
                        align="center",
                        spacing="2",
                    ),
                    width="100%",
                    background="rgba(239,68,68,0.07)",
                    border="1px solid rgba(239,68,68,0.22)",
                    border_radius="12px",
                    padding="13px 16px",
                    margin_top="4px",
                    style={"animation": "fadeSlideUp 0.3s ease both"},
                ),
            ),
            rx.cond(
                AuthState.success_message != "",
                rx.box(
                    rx.hstack(
                        rx.html("""<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>"""),
                        rx.text(AuthState.success_message, color="#a7f3d0", font_size="0.86rem", line_height="1.5"),
                        align="center",
                        spacing="2",
                    ),
                    width="100%",
                    background="rgba(16,185,129,0.07)",
                    border="1px solid rgba(16,185,129,0.22)",
                    border_radius="12px",
                    padding="13px 16px",
                    margin_top="4px",
                    style={"animation": "fadeSlideUp 0.3s ease both"},
                ),
            ),

            # ── Footer ────────────────────────────────────────────────
            rx.text(
                "By signing in you agree to SceneForge's terms of service.",
                color="rgba(113,113,122,0.55)",
                font_size="0.72rem",
                text_align="center",
                line_height="1.7",
                margin_top="8px",
                style={"animation": "fadeSlideUp 0.6s cubic-bezier(0.16,1,0.3,1) 0.55s both"},
            ),

            # ── Card geometry ─────────────────────────────────────────
            width="100%",
            max_width="420px",
            background="rgba(16,16,22,0.7)",
            backdrop_filter="blur(32px) saturate(1.5)",
            border="1px solid rgba(255,255,255,0.07)",
            border_radius="28px",
            padding="56px 44px",
            box_shadow="0 32px 80px -16px rgba(0,0,0,0.75), 0 0 0 1px rgba(255,255,255,0.04), inset 0 1px 0 rgba(255,255,255,0.06)",
            z_index="1",
            style={
                "animation": "fadeSlideUp 0.7s cubic-bezier(0.16,1,0.3,1) both",
                "border-animation": "borderPulse 6s ease-in-out infinite",
            },
        ),

        style=body_style,
    )

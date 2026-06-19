import reflex as rx
from typing import Any, cast
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


def email_auth_form() -> rx.Component:
    return rx.vstack(
        # Heading switch
        rx.heading(
            rx.cond(AuthState.is_signup, "Create Account", "Sign In"),
            size="5",
            color="#f4f4f5",
            font_weight="800",
            letter_spacing="-0.02em",
            margin_bottom="12px",
        ),
        
        # Email field
        rx.vstack(
            rx.text("Email Address", font_size="0.75rem", font_weight="600", color="rgba(161,161,170,0.8)", margin_bottom="4px"),
            rx.hstack(
                rx.html("""<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="rgba(113,113,122,0.6)" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>"""),
                rx.input(
                    placeholder="you@example.com",
                    value=AuthState.email,
                    on_change=cast(Any, AuthState.set_email),
                    border="none",
                    outline="none",
                    color="#f4f4f5",
                    font_size="0.875rem",
                    background="transparent",
                    width="100%",
                    style={"caret-color": "#818cf8"},
                    _placeholder={"color": "rgba(113,113,122,0.5)"},
                ),
                align_items="center",
                gap="8px",
                width="100%",
                background="rgba(255,255,255,0.02)",
                border="1px solid rgba(255,255,255,0.08)",
                border_radius="12px",
                padding="10px 14px",
                _focus_within={
                    "border_color": "rgba(99,102,241,0.5)",
                    "background": "rgba(99,102,241,0.04)",
                },
            ),
            align_items="start",
            width="100%",
            spacing="1",
        ),

        # Password field
        rx.vstack(
            rx.text("Password", font_size="0.75rem", font_weight="600", color="rgba(161,161,170,0.8)", margin_bottom="4px"),
            rx.hstack(
                rx.html("""<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="rgba(113,113,122,0.6)" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>"""),
                rx.input(
                    placeholder="••••••••",
                    type=cast(Any, rx.cond(AuthState.show_password, "text", "password")),
                    value=AuthState.password,
                    on_change=cast(Any, AuthState.set_password),
                    border="none",
                    outline="none",
                    color="#f4f4f5",
                    font_size="0.875rem",
                    background="transparent",
                    width="100%",
                    style={"caret-color": "#818cf8"},
                    _placeholder={"color": "rgba(113,113,122,0.5)"},
                ),
                # Visibility Toggle
                rx.button(
                    rx.cond(
                        AuthState.show_password,
                        rx.html("""<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>"""),
                        rx.html("""<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>"""),
                    ),
                    background="transparent",
                    color="rgba(161,161,170,0.6)",
                    cursor="pointer",
                    padding="0",
                    height="auto",
                    _hover={"color": "white"},
                    on_click=cast(Any, AuthState.toggle_password_visibility),
                ),
                align_items="center",
                gap="8px",
                width="100%",
                background="rgba(255,255,255,0.02)",
                border="1px solid rgba(255,255,255,0.08)",
                border_radius="12px",
                padding="10px 14px",
                _focus_within={
                    "border_color": "rgba(99,102,241,0.5)",
                    "background": "rgba(99,102,241,0.04)",
                },
            ),
            align_items="start",
            width="100%",
            spacing="1",
        ),

        # Confirm Password field (Signup only)
        rx.cond(
            AuthState.is_signup,
            rx.vstack(
                rx.text("Confirm Password", font_size="0.75rem", font_weight="600", color="rgba(161,161,170,0.8)", margin_bottom="4px"),
                rx.hstack(
                    rx.html("""<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="rgba(113,113,122,0.6)" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>"""),
                    rx.input(
                        placeholder="••••••••",
                        type=cast(Any, rx.cond(AuthState.show_password, "text", "password")),
                        value=AuthState.confirm_password,
                        on_change=cast(Any, AuthState.set_confirm_password),
                        border="none",
                        outline="none",
                        color="#f4f4f5",
                        font_size="0.875rem",
                        background="transparent",
                        width="100%",
                        style={"caret-color": "#818cf8"},
                        _placeholder={"color": "rgba(113,113,122,0.5)"},
                    ),
                    align_items="center",
                    gap="8px",
                    width="100%",
                    background="rgba(255,255,255,0.02)",
                    border="1px solid rgba(255,255,255,0.08)",
                    border_radius="12px",
                    padding="10px 14px",
                    _focus_within={
                        "border_color": "rgba(99,102,241,0.5)",
                        "background": "rgba(99,102,241,0.04)",
                    },
                ),
                align_items="start",
                width="100%",
                spacing="1",
            ),
        ),

        # Submit Button
        rx.button(
            rx.cond(
                AuthState.is_loading,
                rx.html("""<div style="width:16px;height:16px;border:2px solid rgba(255,255,255,0.3);border-top-color:white;border-radius:50%;animation:spin-slow 0.8s linear infinite;"></div>"""),
                rx.text(rx.cond(AuthState.is_signup, "Create Account", "Sign In"), font_size="0.95rem", font_weight="700"),
            ),
            background="linear-gradient(135deg, #6366f1, #4f46e5)",
            color="white",
            border_radius="12px",
            width="100%",
            padding_y="12px",
            margin_top="12px",
            cursor="pointer",
            disabled=AuthState.is_loading,
            on_click=cast(Any, AuthState.handle_auth),
            box_shadow="0 4px 14px rgba(99,102,241,0.25)",
            transition="all 0.2s ease",
            _hover={
                "box_shadow": "0 6px 20px rgba(99,102,241,0.4)",
                "transform": "translateY(-1px)",
            },
        ),

        # Switch signup/login link
        rx.button(
            rx.text(rx.cond(AuthState.is_signup, "Already have an account? Sign In", "Don't have an account? Sign Up"), font_size="0.8rem"),
            background="transparent",
            color="#818cf8",
            cursor="pointer",
            border="none",
            _hover={"text_decoration": "underline", "color": "white"},
            on_click=cast(Any, AuthState.toggle_mode),
            margin_top="8px",
        ),

        # Go back to Google OAuth
        rx.button(
            rx.hstack(
                rx.html("""<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>"""),
                rx.text("Back to Google login", font_size="0.8rem"),
                align="center",
                spacing="1",
            ),
            background="transparent",
            color="rgba(161,161,170,0.6)",
            cursor="pointer",
            border="none",
            _hover={"color": "white"},
            on_click=cast(Any, AuthState.toggle_email_form),
            margin_top="16px",
        ),

        width="100%",
        spacing="3",
        align_items="center",
        style={"animation": "fadeIn 0.4s ease both"},
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

            rx.cond(
                AuthState.show_email_form,
                email_auth_form(),
                rx.vstack(
                    # ── Introduction & Security Info ──────────────────────────
                    rx.text(
                        "Sign in or register securely in one click. We verify your identity safely via Google OAuth with zero password requirements.",
                        color="rgba(161,161,170,0.8)",
                        font_size="0.84rem",
                        text_align="center",
                        line_height="1.6",
                        margin_top="12px",
                    ),
                    
                    # ── Google CTA ────────────────────────────────────────────
                    rx.box(
                        rx.button(
                            google_icon(),
                            rx.text("Continue with Google", font_size="0.98rem", font_weight="700", letter_spacing="0.01em"),
                            background="rgba(255, 255, 255, 0.95)",
                            color="#09090b",
                            border_radius="14px",
                            width="100%",
                            padding_y="14px",
                            cursor="pointer",
                            gap="12px",
                            box_shadow="0 4px 14px rgba(255, 255, 255, 0.12), inset 0 1px 0 rgba(255,255,255,0.4)",
                            transition="all 0.25s cubic-bezier(0.16,1,0.3,1)",
                            _hover={
                                "background": "#ffffff",
                                "box_shadow": "0 8px 30px rgba(99, 102, 241, 0.35), 0 0 0 1px rgba(99, 102, 241, 0.15)",
                                "transform": "translateY(-2px)",
                            },
                            _active={"transform": "translateY(0)"},
                            on_click=cast(Any, AuthState.login_with_google),
                            style={"position": "relative", "overflow": "hidden"},
                        ),
                        width="100%",
                        margin_top="8px",
                    ),

                    # ── Switch to Email Form ──────────────────────────────────
                    rx.button(
                        rx.text("Or continue with email and password", font_size="0.82rem"),
                        background="transparent",
                        color="#818cf8",
                        cursor="pointer",
                        border="none",
                        margin_top="16px",
                        _hover={"text_decoration": "underline", "color": "white"},
                        on_click=cast(Any, AuthState.toggle_email_form),
                    ),

                    width="100%",
                    align="center",
                    spacing="3",
                ),
            ),

            # ── Trust & Security Badges ───────────────────────────────
            rx.vstack(
                rx.hstack(
                    rx.html("""<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#818cf8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>"""),
                    rx.text("Secured by Google OAuth", color="rgba(161,161,170,0.7)", font_size="0.75rem", font_weight="600"),
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    rx.html("""<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>"""),
                    rx.text("Automatic secure workspace setup", color="rgba(161,161,170,0.7)", font_size="0.75rem", font_weight="600"),
                    spacing="1",
                    align="center",
                ),
                spacing="2",
                align_items="center",
                margin_top="12px",
                margin_bottom="8px",
                width="100%",
                style={"animation": "fadeSlideUp 0.6s cubic-bezier(0.16,1,0.3,1) 0.4s both"},
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
            rx.box(
                rx.hstack(
                    rx.text("By signing in you agree to SceneForge's ", color="rgba(113,113,122,0.55)", font_size="0.72rem"),
                    rx.link("Terms", href="/terms", color="#818cf8", font_size="0.72rem", text_decoration="none", _hover={"text_decoration": "underline"}),
                    rx.text(" & ", color="rgba(113,113,122,0.55)", font_size="0.72rem"),
                    rx.link("Privacy Policy", href="/privacy", color="#818cf8", font_size="0.72rem", text_decoration="none", _hover={"text_decoration": "underline"}),
                    spacing="1",
                    justify="center",
                    wrap="wrap",
                    margin_top="8px",
                ),
                width="100%",
                style={"animation": "fadeSlideUp 0.6s cubic-bezier(0.16,1,0.3,1) 0.55s both"},
            ),

            # ── Card geometry ─────────────────────────────────────────
            class_name="glass-panel page-transition",
            width="100%",
            max_width="420px",
            border_radius="28px",
            padding="56px 44px",
            z_index="1",
            style={
                "animation": "fadeSlideUp 0.7s cubic-bezier(0.16,1,0.3,1) both",
                "border-animation": "borderPulse 6s ease-in-out infinite",
            },
        ),

        style=body_style,
    )

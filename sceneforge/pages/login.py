import reflex as rx
from sceneforge.state import AuthState

# Custom styles mimicking the premium login.html CSS
body_style = {
    "font_family": "'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif",
    "background_color": "#09090b",
    "min_height": "100vh",
    "color": "#f4f4f5",
    "position": "relative",
    "overflow": "hidden",
    "display": "flex",
    "align_items": "center",
    "justify_content": "center",
}

def ambient_orbs() -> rx.Component:
    """Renders the animated glowing ambient background orbs."""
    return rx.fragment(
        rx.box(
            width="450px",
            height="450px",
            background="radial-gradient(circle, #6366f1, #4f46e5)",
            position="absolute",
            border_radius="50%",
            filter="blur(140px)",
            opacity="0.1",
            top="-100px",
            left="-100px",
            z_index="0",
            pointer_events="none",
        ),
        rx.box(
            width="550px",
            height="550px",
            background="radial-gradient(circle, #a855f7, #7c3aed)",
            position="absolute",
            border_radius="50%",
            filter="blur(140px)",
            opacity="0.1",
            bottom="-150px",
            right="-100px",
            z_index="0",
            pointer_events="none",
        ),
    )

def clapperboard_logo() -> rx.Component:
    """Clapperboard custom SVG logo."""
    return rx.html(
        """
        <svg style="width: 54px; height: 54px; color: #818cf8; filter: drop-shadow(0 0 12px rgba(99, 102, 241, 0.35)); transition: transform 0.3s ease;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20.2 6 3 11l-.9-2.4 17.2-5.1Z"/>
            <path d="M2 12V4a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-4"/>
            <path d="M2 12h20"/>
            <path d="m7 2 2 4"/>
            <path d="m12 2 2 4"/>
            <path d="m17 2 2 4"/>
        </svg>
        """
    )

def google_icon() -> rx.Component:
    """Google OAuth SVG icon."""
    return rx.html(
        """
        <svg style="width: 20px; height: 20px; flex-shrink: 0;" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
            <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
            <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
            <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
            <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
            <path fill="none" d="M0 0h48v48H0z"/>
        </svg>
        """
    )


def login_page() -> rx.Component:
    """The complete visual Login and Signup page."""
    return rx.box(
        ambient_orbs(),
        rx.vstack(
            # Logo & Header
            rx.vstack(
                clapperboard_logo(),
                rx.heading("SceneForge", size="8", margin_top="18px", font_weight="800",
                           background_image="linear-gradient(135deg, #a5b4fc, #c084fc)",
                           background_clip="text", text_fill_color="transparent"),
                rx.text("Film research, powered by AI.", color="#a1a1aa", font_size="0.95rem", text_align="center"),
                rx.text("Upload PDFs. Ask anything. Get sourced answers.", color="#71717a", font_size="0.82rem", text_align="center"),
                align="center",
                spacing="2",
            ),
            
            rx.divider(border_color="rgba(255, 255, 255, 0.06)", margin_y="24px"),
            
            # Auth Form (Email/Password)
            rx.form(
                rx.vstack(
                    rx.vstack(
                        rx.text("Email Address", font_size="0.82rem", color="#a1a1aa", font_weight="600", text_transform="uppercase", letter_spacing="0.05em", width="100%"),
                        rx.input(
                            placeholder="you@example.com",
                            type="email",
                            value=AuthState.email,
                            on_change=AuthState.set_email,
                            required=True,
                            width="100%",
                            background="rgba(255, 255, 255, 0.03)",
                            border="1px solid rgba(255, 255, 255, 0.08)",
                            border_radius="12px",
                            padding="12px 16px",
                            color="#f4f4f5",
                            _focus={"border_color": "rgba(99, 102, 241, 0.5)", "background": "rgba(255, 255, 255, 0.05)"}
                        ),
                        width="100%",
                        align_items="start",
                    ),
                    rx.vstack(
                        rx.text("Password", font_size="0.82rem", color="#a1a1aa", font_weight="600", text_transform="uppercase", letter_spacing="0.05em", width="100%"),
                        rx.input(
                            placeholder="••••••••",
                            type="password",
                            value=AuthState.password,
                            on_change=AuthState.set_password,
                            required=True,
                            min_length=6,
                            width="100%",
                            background="rgba(255, 255, 255, 0.03)",
                            border="1px solid rgba(255, 255, 255, 0.08)",
                            border_radius="12px",
                            padding="12px 16px",
                            color="#f4f4f5",
                            _focus={"border_color": "rgba(99, 102, 241, 0.5)", "background": "rgba(255, 255, 255, 0.05)"}
                        ),
                        width="100%",
                        align_items="start",
                    ),
                    rx.button(
                        rx.cond(AuthState.is_signup, "Sign Up", "Sign In"),
                        type="submit",
                        width="100%",
                        padding_y="22px",
                        background="linear-gradient(135deg, #6366f1, #4f46e5)",
                        color="#ffffff",
                        border_radius="12px",
                        font_size="0.98rem",
                        font_weight="700",
                        cursor="pointer",
                        _hover={"box_shadow": "0 6px 20px rgba(99, 102, 241, 0.4)", "opacity": "0.95"},
                    ),
                    spacing="4",
                    width="100%",
                ),
                on_submit=AuthState.handle_auth,
                width="100%",
            ),

            # Or Divider
            rx.hstack(
                rx.box(height="1px", flex="1", background_color="rgba(255, 255, 255, 0.06)"),
                rx.text("or", font_size="0.78rem", color="#71717a", text_transform="uppercase", letter_spacing="0.05em"),
                rx.box(height="1px", flex="1", background_color="rgba(255, 255, 255, 0.06)"),
                width="100%",
                align="center",
                margin_y="20px",
            ),
            
            # Google Sign In (Note: Requires dashboard configuration)
            rx.button(
                google_icon(),
                rx.text("Continue with Google", font_size="0.98rem", font_weight="600"),
                background_color="#18181b",
                color="#f4f4f5",
                border="1px solid rgba(255, 255, 255, 0.1)",
                border_radius="12px",
                width="100%",
                padding_y="22px",
                cursor="pointer",
                _hover={"background_color": "#27272a", "border_color": "rgba(99, 102, 241, 0.4)", "box_shadow": "0 8px 24px rgba(99, 102, 241, 0.15)"},
                # For demo, Google login triggers toast or error if not configured
                on_click=lambda: rx.toast.info("Google OAuth is not configured on this workspace. Please use Email/Password sign-in.")
            ),

            # Toggle Sign In / Sign Up
            rx.hstack(
                rx.text(rx.cond(AuthState.is_signup, "Already have an account?", "Don't have an account?"), color="#a1a1aa", font_size="0.88rem"),
                rx.link(
                    rx.cond(AuthState.is_signup, "Sign In", "Sign Up"),
                    on_click=AuthState.toggle_mode,
                    color="#818cf8",
                    font_weight="600",
                    text_decoration="none",
                    _hover={"color": "#a5b4fc"},
                ),
                margin_top="24px",
            ),

            # Error Alert
            rx.cond(
                AuthState.error_message != "",
                rx.box(
                    rx.hstack(
                        rx.icon("triangle_alert", size=18, color="#f87171"),
                        rx.text(AuthState.error_message, color="#fca5a5", font_size="0.88rem"),
                        align="center",
                        spacing="2",
                    ),
                    width="100%",
                    background_color="rgba(239, 68, 68, 0.08)",
                    border="1px solid rgba(239, 68, 68, 0.2)",
                    border_radius="12px",
                    padding="14px 18px",
                    margin_top="20px",
                )
            ),

            # Success Alert
            rx.cond(
                AuthState.success_message != "",
                rx.box(
                    rx.hstack(
                        rx.icon("circle_check", size=18, color="#34d399"),
                        rx.text(AuthState.success_message, color="#a7f3d0", font_size="0.88rem"),
                        align="center",
                        spacing="2",
                    ),
                    width="100%",
                    background_color="rgba(16, 185, 129, 0.08)",
                    border="1px solid rgba(16, 185, 129, 0.2)",
                    border_radius="12px",
                    padding="14px 18px",
                    margin_top="20px",
                )
            ),

            # Footer Terms
            rx.text(
                "By signing in you agree to SceneForge's terms of service. Your account details are used only for authentication.",
                color="#71717a",
                font_size="0.75rem",
                text_align="center",
                line_height="1.6",
                margin_top="32px",
            ),

            # Card Container Properties
            width="100%",
            max_width="420px",
            background_color="rgba(24, 24, 27, 0.45)",
            backdrop_filter="blur(24px)",
            border="1px solid rgba(255, 255, 255, 0.08)",
            border_radius="24px",
            padding="56px 40px",
            box_shadow="0 24px 60px -15px rgba(0, 0, 0, 0.7)",
            z_index="1",
        ),
        style=body_style,
    )

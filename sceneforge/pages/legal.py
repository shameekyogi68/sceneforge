import reflex as rx
from sceneforge.styles import GLOBAL_CSS, BACKGROUND_COLOR, SURFACE_COLOR, ACCENT_COLOR, TEXT_COLOR, MUTED_COLOR, FONT_FAMILY

body_style = {
    "font_family": FONT_FAMILY,
    "background_color": BACKGROUND_COLOR,
    "min_height": "100vh",
    "color": TEXT_COLOR,
    "position": "relative",
    "overflow_x": "hidden",
    "display": "flex",
    "align_items": "center",
    "justify_content": "center",
    "padding": "40px 20px",
}

KEYFRAMES = """
@keyframes floatOrb {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50%       { transform: translate(40px, -30px) scale(1.05); }
}
@keyframes floatOrb2 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50%       { transform: translate(-30px, 40px) scale(1.05); }
}
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes shimmerText {
  0%   { text-shadow: 0 0 5px #00F0FF, 0 0 10px #00F0FF; }
  50%  { text-shadow: 0 0 20px #00F0FF, 0 0 30px #00F0FF; }
  100% { text-shadow: 0 0 5px #00F0FF, 0 0 10px #00F0FF; }
}
"""

def ambient_background() -> rx.Component:
    return rx.fragment(
        rx.box(
            width="500px",
            height="500px",
            background="radial-gradient(circle at center, rgba(0,240,255,0.15) 0%, transparent 70%)",
            position="absolute",
            border_radius="50%",
            filter="blur(80px)",
            opacity="0.15",
            top="-150px",
            left="-150px",
            z_index="0",
            pointer_events="none",
            style={"animation": "floatOrb 15s ease-in-out infinite"},
        ),
        rx.box(
            width="500px",
            height="500px",
            background="radial-gradient(circle at center, rgba(0,180,255,0.06) 0%, transparent 70%)",
            position="absolute",
            border_radius="50%",
            filter="blur(80px)",
            opacity="0.12",
            bottom="-150px",
            right="-150px",
            z_index="0",
            pointer_events="none",
            style={"animation": "floatOrb2 18s ease-in-out infinite"},
        ),
    )

def legal_card(title: str, content: rx.Component) -> rx.Component:
    return rx.box(
        rx.html(f"<style>{GLOBAL_CSS}{KEYFRAMES}</style>"),
        ambient_background(),
        rx.vstack(
            # Back to Login Link
            rx.link(
                rx.hstack(
                    rx.html("""<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>"""),
                    rx.text("BACK TO LOGIN", font_size="0.84rem", font_weight="600"),
                    align="center",
                    spacing="1",
                ),
                href="/login",
                color=MUTED_COLOR,
                text_decoration="none",
                transition="all 0.2s ease",
                _hover={"color": ACCENT_COLOR, "text_decoration": "none", "text_shadow": f"0 0 8px {ACCENT_COLOR}"},
                margin_bottom="24px",
            ),
            
            # Heading
            rx.heading(
                title.upper(),
                size="7",
                font_weight="800",
                letter_spacing="0.1em",
                margin_bottom="16px",
                style={
                    "color": "#fff",
                    "font_family": "'Plus Jakarta Sans', sans-serif",
                }
            ),
            
            # Divider
            rx.box(
                height="1px",
                width="100%",
                background=f"rgba(0,240,255,0.2)",
                margin_bottom="24px",
            ),
            
            # Content
            content,
            
            align_items="start",
            width="100%",
        ),
        width="100%",
        max_width="720px",
        class_name="glass-panel-glow",
        padding="48px",
        z_index="1",
        position="relative",
        style={"animation": "fadeSlideUp 0.6s cubic-bezier(0.16,1,0.3,1) both"},
    )

def terms_page() -> rx.Component:
    terms_content = rx.vstack(
        rx.text("Welcome to ScriptIQ. By using our services, you agree to comply with and be bound by the following terms of service. Please review them carefully.", color=TEXT_COLOR, font_size="0.92rem", line_height="1.6"),
        rx.heading("1. Acceptable Use", size="4", font_weight="700", color="#fff", margin_top="16px", letter_spacing="0.02em", font_family="'Plus Jakarta Sans', sans-serif"),
        rx.text("You agree to use ScriptIQ only for lawful purposes related to research. You may not upload malicious documents or attempt to exploit the service or database.", color=MUTED_COLOR, font_size="0.88rem", line_height="1.6"),
        rx.heading("2. Intellectual Property", size="4", font_weight="700", color="#fff", margin_top="16px", letter_spacing="0.02em", font_family="'Plus Jakarta Sans', sans-serif"),
        rx.text("The uploaded research documents are owned by their respective copyright holders. ScriptIQ processes the documents solely to provide retrieval-augmented answers to the uploading user.", color=MUTED_COLOR, font_size="0.88rem", line_height="1.6"),
        rx.heading("3. AI Limitations", size="4", font_weight="700", color="#fff", margin_top="16px", letter_spacing="0.02em", font_family="'Plus Jakarta Sans', sans-serif"),
        rx.text("While ScriptIQ incorporates zero-hallucination prompting and vector search, AI models may occasionally produce incomplete or inaccurate answers. Users should verify critical sources directly.", color=MUTED_COLOR, font_size="0.88rem", line_height="1.6"),
        rx.heading("4. Account Use & Terms", size="4", font_weight="700", color="#fff", margin_top="16px", letter_spacing="0.02em", font_family="'Plus Jakarta Sans', sans-serif"),
        rx.text("We reserve the right to suspend or terminate accounts that exceed fair use policies (e.g. rate limit bypassing) or violate acceptable use guidelines.", color=MUTED_COLOR, font_size="0.88rem", line_height="1.6"),
        spacing="4",
        align_items="start",
    )
    return rx.box(
        legal_card("Terms of Service", terms_content),
        style=body_style,
    )


def privacy_page() -> rx.Component:
    privacy_content = rx.vstack(
        rx.text("At ScriptIQ, we value your privacy. This policy outlines how we handle your personal data and uploaded documents.", color=TEXT_COLOR, font_size="0.92rem", line_height="1.6"),
        rx.heading("1. Data Collected", size="4", font_weight="700", color="#fff", margin_top="16px", letter_spacing="0.02em", font_family="'Plus Jakarta Sans', sans-serif"),
        rx.text("We collect your email address for account authentication and user session management. Uploaded documents are stored securely in Supabase Storage.", color=MUTED_COLOR, font_size="0.88rem", line_height="1.6"),
        rx.heading("2. Document Security", size="4", font_weight="700", color="#fff", margin_top="16px", letter_spacing="0.02em", font_family="'Plus Jakarta Sans', sans-serif"),
        rx.text("Your documents and corresponding embedded chunks are privately linked to your user account. No other users can access your documents or view your chat history.", color=MUTED_COLOR, font_size="0.88rem", line_height="1.6"),
        rx.heading("3. Third-Party Services", size="4", font_weight="700", color="#fff", margin_top="16px", letter_spacing="0.02em", font_family="'Plus Jakarta Sans', sans-serif"),
        rx.text("To generate responses, queries are processed by the Gemini API. We do not share your documents with third parties for training purposes.", color=MUTED_COLOR, font_size="0.88rem", line_height="1.6"),
        rx.heading("4. Cookies", size="4", font_weight="700", color="#fff", margin_top="16px", letter_spacing="0.02em", font_family="'Plus Jakarta Sans', sans-serif"),
        rx.text("ScriptIQ uses secure, same-site cookies to maintain your login session. No cross-site tracking cookies are utilized.", color=MUTED_COLOR, font_size="0.88rem", line_height="1.6"),
        spacing="4",
        align_items="start",
    )
    return rx.box(
        legal_card("Privacy Policy", privacy_content),
        style=body_style,
    )

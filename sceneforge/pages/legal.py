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
            background="radial-gradient(circle at center, rgba(255,0,85,0.1) 0%, transparent 70%)",
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
        rx.box(
            position="absolute",
            top="0", left="0", right="0", bottom="0",
            background="linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px)",
            background_size="100% 4px",
            z_index="0",
            pointer_events="none",
            opacity="0.4",
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
                    rx.text("SYS.BACK_TO_LOGIN", font_size="0.84rem", font_weight="600"),
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
                    "animation": "shimmerText 3s linear infinite",
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
        background="rgba(5,8,15,0.85)",
        backdrop_filter="blur(10px)",
        border=f"1px solid {ACCENT_COLOR}",
        border_radius="4px",
        padding="48px",
        box_shadow=f"0 0 20px rgba(0,240,255,0.1), inset 0 0 20px rgba(0,240,255,0.05)",
        z_index="1",
        position="relative",
        style={"animation": "fadeSlideUp 0.6s cubic-bezier(0.16,1,0.3,1) both"},
        _before={
            "content": '""',
            "position": "absolute",
            "top": "0", "left": "0", "right": "0", "bottom": "0",
            "background": "linear-gradient(rgba(0, 240, 255, 0.05) 1px, transparent 1px)",
            "background_size": "100% 3px",
            "pointer_events": "none",
            "z_index": "10",
            "opacity": "0.3",
        }
    )

def terms_page() -> rx.Component:
    terms_content = rx.vstack(
        rx.text("Welcome to ScriptIQ. By using our services, you agree to comply with and be bound by the following terms of service. Please review them carefully.", color=TEXT_COLOR, font_size="0.92rem", line_height="1.6"),
        rx.heading("1. ACCEPTABLE_USE", size="4", font_weight="700", color="#fff", margin_top="16px", letter_spacing="0.05em"),
        rx.text("You agree to use ScriptIQ only for lawful purposes related to research. You may not upload malicious documents or attempt to exploit the service or database.", color=MUTED_COLOR, font_size="0.88rem", line_height="1.6"),
        rx.heading("2. INTELLECTUAL_PROPERTY", size="4", font_weight="700", color="#fff", margin_top="16px", letter_spacing="0.05em"),
        rx.text("The uploaded research documents are owned by their respective copyright holders. ScriptIQ processes the documents solely to provide retrieval-augmented answers to the uploading user.", color=MUTED_COLOR, font_size="0.88rem", line_height="1.6"),
        rx.heading("3. AI_LIMITATIONS", size="4", font_weight="700", color="#fff", margin_top="16px", letter_spacing="0.05em"),
        rx.text("While ScriptIQ incorporates zero-hallucination prompting and vector search, AI models may occasionally produce incomplete or inaccurate answers. Users should verify critical sources directly.", color=MUTED_COLOR, font_size="0.88rem", line_height="1.6"),
        rx.heading("4. TERMINATION", size="4", font_weight="700", color="#fff", margin_top="16px", letter_spacing="0.05em"),
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
        rx.heading("1. DATA_COLLECTED", size="4", font_weight="700", color="#fff", margin_top="16px", letter_spacing="0.05em"),
        rx.text("We collect your email address for account authentication and user session management. Uploaded documents are stored securely in Supabase Storage.", color=MUTED_COLOR, font_size="0.88rem", line_height="1.6"),
        rx.heading("2. DOCUMENT_SECURITY", size="4", font_weight="700", color="#fff", margin_top="16px", letter_spacing="0.05em"),
        rx.text("Your documents and corresponding embedded chunks are privately linked to your user account. No other users can access your documents or view your chat history.", color=MUTED_COLOR, font_size="0.88rem", line_height="1.6"),
        rx.heading("3. THIRD_PARTY_APIS", size="4", font_weight="700", color="#fff", margin_top="16px", letter_spacing="0.05em"),
        rx.text("To generate responses, queries are processed by the Gemini API. We do not share your documents with third parties for training purposes.", color=MUTED_COLOR, font_size="0.88rem", line_height="1.6"),
        rx.heading("4. COOKIES", size="4", font_weight="700", color="#fff", margin_top="16px", letter_spacing="0.05em"),
        rx.text("ScriptIQ uses secure, same-site cookies to maintain your login session. No cross-site tracking cookies are utilized.", color=MUTED_COLOR, font_size="0.88rem", line_height="1.6"),
        spacing="4",
        align_items="start",
    )
    return rx.box(
        legal_card("Privacy Policy", privacy_content),
        style=body_style,
    )

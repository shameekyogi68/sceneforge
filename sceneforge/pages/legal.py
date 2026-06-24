import reflex as rx
from sceneforge.styles import GLOBAL_CSS

body_style = {
    "font_family": "'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif",
    "background_color": "#080810",
    "min_height": "100vh",
    "color": "#f4f4f5",
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
"""

def ambient_background() -> rx.Component:
    return rx.fragment(
        rx.box(
            width="500px",
            height="500px",
            background="radial-gradient(circle at center, rgba(99,102,241,0.4) 0%, transparent 70%)",
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
            background="radial-gradient(circle at center, rgba(168,85,247,0.3) 0%, transparent 70%)",
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
                    rx.text("Back to Login", font_size="0.84rem", font_weight="600"),
                    align="center",
                    spacing="1",
                ),
                href="/login",
                color="rgba(161,161,170,0.8)",
                text_decoration="none",
                _hover={"color": "#a5b4fc", "text_decoration": "none"},
                margin_bottom="24px",
            ),
            
            # Heading
            rx.heading(
                title,
                size="7",
                font_weight="800",
                letter_spacing="-0.03em",
                margin_bottom="16px",
                style={
                    "background": "linear-gradient(135deg, #c7d2fe 0%, #a5b4fc 50%, #c084fc 100%)",
                    "-webkit-background-clip": "text",
                    "-webkit-text-fill-color": "transparent",
                    "background-clip": "text",
                }
            ),
            
            # Divider
            rx.box(
                height="1px",
                width="100%",
                background="rgba(255,255,255,0.08)",
                margin_bottom="24px",
            ),
            
            # Content
            content,
            
            align_items="start",
            width="100%",
        ),
        width="100%",
        max_width="720px",
        background="rgba(16,16,22,0.75)",
        backdrop_filter="blur(32px) saturate(1.5)",
        border="1px solid rgba(255,255,255,0.07)",
        border_radius="24px",
        padding="48px",
        box_shadow="0 32px 80px -16px rgba(0,0,0,0.8), 0 0 0 1px rgba(255,255,255,0.02)",
        z_index="1",
        style={"animation": "fadeSlideUp 0.6s cubic-bezier(0.16,1,0.3,1) both"},
    )

def terms_page() -> rx.Component:
    terms_content = rx.vstack(
        rx.text("Welcome to tselaf. By using our services, you agree to comply with and be bound by the following terms of service. Please review them carefully.", color="rgba(212,212,216,0.9)", font_size="0.92rem", line_height="1.6"),
        rx.heading("1. Acceptable Use", size="4", font_weight="700", color="#f4f4f5", margin_top="16px"),
        rx.text("You agree to use tselaf only for lawful purposes related to film research. You may not upload malicious documents or attempt to exploit the service or database.", color="rgba(161,161,170,0.9)", font_size="0.88rem", line_height="1.6"),
        rx.heading("2. Intellectual Property", size="4", font_weight="700", color="#f4f4f5", margin_top="16px"),
        rx.text("The uploaded research documents are owned by their respective copyright holders. tselaf processes the documents solely to provide retrieval-augmented answers to the uploading user.", color="rgba(161,161,170,0.9)", font_size="0.88rem", line_height="1.6"),
        rx.heading("3. AI Limitations", size="4", font_weight="700", color="#f4f4f5", margin_top="16px"),
        rx.text("While tselaf incorporates zero-hallucination prompting and vector search, AI models may occasionally produce incomplete or inaccurate answers. Users should verify critical sources directly.", color="rgba(161,161,170,0.9)", font_size="0.88rem", line_height="1.6"),
        rx.heading("4. Terminations", size="4", font_weight="700", color="#f4f4f5", margin_top="16px"),
        rx.text("We reserve the right to suspend or terminate accounts that exceed fair use policies (e.g. rate limit bypassing) or violate acceptable use guidelines.", color="rgba(161,161,170,0.9)", font_size="0.88rem", line_height="1.6"),
        spacing="4",
        align_items="start",
    )
    return rx.box(
        legal_card("Terms of Service", terms_content),
        style=body_style,
    )


def privacy_page() -> rx.Component:
    privacy_content = rx.vstack(
        rx.text("At tselaf, we value your privacy. This policy outlines how we handle your personal data and uploaded documents.", color="rgba(212,212,216,0.9)", font_size="0.92rem", line_height="1.6"),
        rx.heading("1. Data Collected", size="4", font_weight="700", color="#f4f4f5", margin_top="16px"),
        rx.text("We collect your email address for account authentication and user session management. Uploaded documents are stored securely in Supabase Storage.", color="rgba(161,161,170,0.9)", font_size="0.88rem", line_height="1.6"),
        rx.heading("2. Document Security", size="4", font_weight="700", color="#f4f4f5", margin_top="16px"),
        rx.text("Your documents and corresponding embedded chunks are privately linked to your user account. No other users can access your documents or view your chat history.", color="rgba(161,161,170,0.9)", font_size="0.88rem", line_height="1.6"),
        rx.heading("3. Third-party APIs", size="4", font_weight="700", color="#f4f4f5", margin_top="16px"),
        rx.text("To generate responses, queries are processed by the Gemini API. We do not share your documents with third parties for training purposes.", color="rgba(161,161,170,0.9)", font_size="0.88rem", line_height="1.6"),
        rx.heading("4. Cookies", size="4", font_weight="700", color="#f4f4f5", margin_top="16px"),
        rx.text("tselaf uses secure, same-site cookies to maintain your login session. No cross-site tracking cookies are utilized.", color="rgba(161,161,170,0.9)", font_size="0.88rem", line_height="1.6"),
        spacing="4",
        align_items="start",
    )
    return rx.box(
        legal_card("Privacy Policy", privacy_content),
        style=body_style,
    )

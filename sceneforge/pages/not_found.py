import reflex as rx
from typing import Any, cast
from sceneforge.styles import ACCENT_COLOR, BACKGROUND_COLOR, GLOBAL_CSS, SCREENPLAY_FONT_FAMILY
from sceneforge.pages.navigation import app_icon

KEYFRAMES_404 = """
@keyframes floatOrb404 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50%       { transform: translate(-30px, 40px) scale(1.05); }
}
@keyframes fadeSlideUp404 {
  from { opacity: 0; transform: translateY(30px); }
  to   { opacity: 1; transform: translateY(0); }
}
"""

def ambient_orbs_404() -> rx.Component:
    return rx.fragment(
        rx.box(
            width="500px", height="500px",
            background="radial-gradient(circle at center, rgba(255,0,85,0.06) 0%, transparent 70%)",
            position="absolute", border_radius="50%", filter="blur(80px)",
            top="10%", left="-5%", z_index="0", pointer_events="none",
            style={"animation": "floatOrb404 15s ease-in-out infinite"},
        ),
        rx.box(
            width="600px", height="600px",
            background="radial-gradient(circle at center, rgba(0,240,255,0.06) 0%, transparent 70%)",
            position="absolute", border_radius="50%", filter="blur(90px)",
            bottom="10%", right="-5%", z_index="0", pointer_events="none",
            style={"animation": "floatOrb404 20s ease-in-out infinite reverse"},
        ),
    )

def not_found_page() -> rx.Component:
    return rx.box(
        rx.html(f"<style>{GLOBAL_CSS}{KEYFRAMES_404}</style>"),
        ambient_orbs_404(),
        
        rx.center(
            rx.vstack(
                # App logo
                app_icon(size="48px", icon_size="20px"),
                
                # 404 Card
                rx.vstack(
                    rx.heading(
                        "ERROR_404",
                        size="9",
                        font_family="'Courier Prime', 'Courier New', Courier, monospace",
                        color="#FF0055",
                        style={"text_shadow": "0 0 20px rgba(255, 0, 85, 0.45)"},
                        margin_bottom="4px",
                    ),
                    rx.text(
                        "PAGE NOT FOUND OR UNRESOLVED DIRECTORY",
                        class_name="hud-text",
                        font_size="0.65rem",
                        color="rgba(255,255,255,0.45)",
                        letter_spacing="0.12em",
                        margin_bottom="12px",
                    ),
                    rx.box(
                        width="100%", height="1px", 
                        background="linear-gradient(90deg, transparent, rgba(255,0,85,0.25), transparent)", 
                        margin_y="8px"
                    ),
                    rx.text(
                        "The screenplay draft or resource you are looking for does not exist or has been deleted.",
                        color="rgba(226, 232, 240, 0.7)",
                        font_size="0.85rem",
                        text_align="center",
                        line_height="1.6",
                        max_width="320px",
                        margin_top="10px",
                    ),
                    rx.button(
                        rx.hstack(
                            rx.html("""<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>"""),
                            rx.text("Return to Dashboard", font_size="0.85rem", font_weight="700"),
                            spacing="2",
                            align_items="center",
                        ),
                        on_click=rx.redirect("/dashboard"),
                        background="rgba(0, 240, 255, 0.05)",
                        color="#00F0FF",
                        border="1px solid rgba(0, 240, 255, 0.3)",
                        border_radius="100px",
                        padding="12px 24px",
                        cursor="pointer",
                        margin_top="24px",
                        box_shadow="0 0 15px rgba(0, 240, 255, 0.1)",
                        transition="all 0.2s ease",
                        _hover={
                            "background": "rgba(0, 240, 255, 0.12)",
                            "border_color": "#00F0FF",
                            "box_shadow": "0 0 25px rgba(0, 240, 255, 0.35)",
                            "transform": "translateY(-1px)",
                        },
                        _active={"transform": "scale(0.98)"},
                    ),
                    class_name="glass-panel-glow page-transition",
                    align_items="center",
                    padding="48px 36px",
                    border_radius="20px",
                    max_width="440px",
                    width="100%",
                    style={
                        "animation": "fadeSlideUp404 0.6s cubic-bezier(0.16,1,0.3,1) both",
                        "box_shadow": "0 20px 50px rgba(0,0,0,0.6), 0 0 30px rgba(255, 0, 85, 0.04)",
                        "border_color": "rgba(255, 0, 85, 0.15)",
                    },
                ),
                spacing="6",
                align_items="center",
                width="100%",
            ),
            width="100vw",
            height="100vh",
            background_color=BACKGROUND_COLOR,
            z_index="1",
        ),
        width="100vw",
        height="100vh",
        background_color=BACKGROUND_COLOR,
        position="relative",
        overflow="hidden",
    )

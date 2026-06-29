import reflex as rx
from sceneforge.styles import ACCENT_COLOR, BACKGROUND_COLOR, GLOBAL_CSS


def not_found_page() -> rx.Component:
    return rx.box(
        rx.html(f"<style>{GLOBAL_CSS}</style>"),
        rx.center(
            rx.vstack(
                rx.heading(
                    "404",
                    size="9",
                    font_family="'Courier Prime', 'Courier New', Courier, monospace",
                    color=ACCENT_COLOR,
                    style={"text_shadow": "0 0 20px rgba(0, 240, 255, 0.4)"},
                ),
                rx.text(
                    "This page does not exist.",
                    color="rgba(226, 232, 240, 0.7)",
                    font_size="1rem",
                ),
                rx.button(
                    rx.text("Return to Dashboard", font_weight="600"),
                    on_click=rx.redirect("/dashboard"),
                    background="rgba(0, 240, 255, 0.1)",
                    border=f"1px solid {ACCENT_COLOR}",
                    color=ACCENT_COLOR,
                    _hover={"background": "rgba(0, 240, 255, 0.2)", "box_shadow": "0 0 15px rgba(0, 240, 255, 0.3)"},
                    margin_top="24px",
                ),
                spacing="4",
                align_items="center",
            ),
            width="100vw",
            height="100vh",
            background_color=BACKGROUND_COLOR,
        ),
        width="100vw",
        height="100vh",
        background_color=BACKGROUND_COLOR,
    )

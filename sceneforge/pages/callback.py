import reflex as rx
from sceneforge.state import AuthState

def callback_page() -> rx.Component:
    """A minimal fallback page shown briefly during OAuth token extraction."""
    return rx.center(
        rx.vstack(
            rx.spinner(size="3", color="indigo"),
            rx.text("Completing Google Sign-in...", color="#a1a1aa", font_size="1rem", font_weight="600"),
            align="center",
            spacing="3",
        ),
        height="100vh",
        background_color="#09090b",
        width="100%",
    )

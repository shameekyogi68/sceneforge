import reflex as rx
from typing import Any
from sceneforge.state import DashboardState


body_style = {
    "font_family": "'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif",
    "background_color": "#09090b",
    "min_height": "100vh",
    "color": "#f4f4f5",
    "position": "relative",
    "overflow_x": "hidden",
}

def header_bar() -> rx.Component:
    """Header bar with user profile and Sign Out."""
    return rx.hstack(
        rx.link(
            rx.hstack(
                rx.icon("clapperboard", size=26, color="#818cf8"),
                rx.text("SceneForge", font_size="1.3rem", font_weight="800",
                        background_image="linear-gradient(135deg, #a5b4fc, #c084fc)",
                        background_clip="text", text_fill_color="transparent"),
                align="center",
                spacing="2",
            ),
            href="/dashboard",
            text_decoration="none",
        ),
        rx.hstack(
            rx.box(
                rx.text(DashboardState.user_avatar_char),
                width="32px",
                height="32px",
                border_radius="50%",
                background="linear-gradient(135deg, #6366f1, #a855f7)",
                color="white",
                display="flex",
                align_items="center",
                justify_content="center",
                font_weight="700",
                font_size="0.9rem",
                box_shadow="0 0 10px rgba(99, 102, 241, 0.3)",
                text_transform="uppercase",
            ),
            rx.text(DashboardState.user_email, font_size="0.85rem", color="#a1a1aa", font_weight="500"),
            rx.button(
                rx.icon("log_out", size=15),
                rx.text("Sign Out"),
                background_color="rgba(255, 255, 255, 0.03)",
                border="1px solid rgba(255, 255, 255, 0.08)",
                color="#d4d4d8",
                border_radius="10px",
                padding="8px 16px",
                font_size="0.85rem",
                font_weight="600",
                cursor="pointer",
                _hover={"background_color": "rgba(239, 68, 68, 0.08)", "border_color": "rgba(239, 68, 68, 0.25)", "color": "#fca5a5"},
                on_click=DashboardState.logout,
            ),
            align="center",
            spacing="3",
            margin_left="auto",
        ),
        width="100%",
        padding="16px 40px",
        background_color="rgba(9, 9, 11, 0.65)",
        backdrop_filter="blur(24px)",
        border_bottom="1px solid rgba(255, 255, 255, 0.08)",
        position="sticky",
        top="0",
        z_index="10",
    )

def render_project_card(proj: Any) -> rx.Component:
    formatted_date = proj["created_date"]
    return rx.box(
        # Delete project button
        rx.button(
            rx.icon("trash_2", size=14),
            position="absolute",
            top="22px",
            right="22px",
            background_color="rgba(239, 68, 68, 0.05)",
            border="1px solid rgba(239, 68, 68, 0.15)",
            color="#fca5a5",
            border_radius="8px",
            padding="6px",
            cursor="pointer",
            opacity="0.8", # visible in reflex always, styled nicely
            _hover={"background_color": "#ef4444", "border_color": "#ef4444", "color": "#ffffff", "transform": "scale(1.08)"},
            on_click=lambda: DashboardState.delete_project(proj["id"], proj["name"]),
        ),
        # Card Body
        rx.vstack(
            rx.box(
                rx.icon("folder_closed", size=22),
                width="44px",
                height="44px",
                border_radius="12px",
                background_color="rgba(99, 102, 241, 0.08)",
                border="1px solid rgba(99, 102, 241, 0.15)",
                color="#818cf8",
                display="flex",
                align_items="center",
                justify_content="center",
                margin_bottom="16px",
            ),
            rx.text(proj["name"], font_size="1.15rem", font_weight="700", color="#f4f4f5", word_break="break-all"),
            rx.text("Created ", formatted_date, font_size="0.82rem", color="#71717a"),
            spacing="1",
            align_items="start",
        ),
        background_color="rgba(24, 24, 27, 0.4)",
        border="1px solid rgba(255, 255, 255, 0.06)",
        border_radius="20px",
        padding="28px",
        cursor="pointer",
        position="relative",
        backdrop_filter="blur(16px)",
        _hover={
            "transform": "translateY(-4px)",
            "background_color": "rgba(99, 102, 241, 0.04)",
            "border_color": "rgba(99, 102, 241, 0.4)",
            "box_shadow": "0 16px 36px rgba(99, 102, 241, 0.08)",
        },
        transition="all 0.3s cubic-bezier(0.16, 1, 0.3, 1)",
        on_click=lambda: rx.redirect(f"/project?project_id={proj['id']}"),
    )

def dashboard_page() -> rx.Component:
    """The main Dashboard Page view."""
    return rx.box(
        header_bar(),
        # Ambient glow orbs
        rx.box(
            width="500px",
            height="500px",
            background="radial-gradient(circle, #6366f1, #4f46e5)",
            position="absolute",
            border_radius="50%",
            filter="blur(150px)",
            opacity="0.06",
            top="-200px",
            left="-100px",
            z_index="0",
            pointer_events="none",
        ),
        rx.box(
            width="600px",
            height="600px",
            background="radial-gradient(circle, #a855f7, #7c3aed)",
            position="absolute",
            border_radius="50%",
            filter="blur(150px)",
            opacity="0.06",
            bottom="-200px",
            right="-100px",
            z_index="0",
            pointer_events="none",
        ),
        
        # Main content
        rx.vstack(
            rx.heading("Your Projects", size="7", font_weight="800", color="#f4f4f5", letter_spacing="-0.03em"),
            rx.text("Each project holds its own research documents and chat history.", color="#a1a1aa", font_size="0.95rem", margin_bottom="30px"),
            
            # Toolbar
            rx.hstack(
                rx.hstack(
                    rx.icon("search", size=18, color="#71717a"),
                    rx.input(
                        placeholder="Search projects...",
                        value=DashboardState.search_query,
                        on_change=DashboardState.set_search_query,
                        border="none",
                        outline="none",
                        color="#f4f4f5",
                        font_size="0.9rem",
                        background="transparent",
                        width="100%",
                    ),
                    background="rgba(255, 255, 255, 0.03)",
                    border="1px solid rgba(255, 255, 255, 0.08)",
                    border_radius="12px",
                    padding="6px 12px",
                    width="100%",
                    max_width="360px",
                    align_items="center",
                ),
                rx.button(
                    rx.icon("plus", size=16),
                    rx.text("New Project"),
                    background="linear-gradient(135deg, #6366f1, #4f46e5)",
                    color="white",
                    border_radius="12px",
                    padding="11px 22px",
                    font_size="0.9rem",
                    font_weight="700",
                    cursor="pointer",
                    box_shadow="0 4px 14px rgba(99, 102, 241, 0.25)",
                    _hover={"box_shadow": "0 6px 20px rgba(99, 102, 241, 0.45)", "transform": "translateY(-2px)"},
                    _active={"transform": "translateY(1px)"},
                    on_click=DashboardState.open_modal,
                ),
                width="100%",
                justify="between",
                align_items="center",
                margin_bottom="28px",
            ),
            
            # Projects Grid
            rx.cond(
                DashboardState.filtered_projects.length() > 0,
                rx.grid(
                    rx.foreach(DashboardState.filtered_projects, render_project_card),
                    columns=rx.breakpoints(initial="1", sm="2", md="3"),
                    spacing="5",
                    width="100%",
                ),
                # Empty State
                rx.vstack(
                    rx.box(
                        rx.icon("film", size=36),
                        width="72px",
                        height="72px",
                        border_radius="20px",
                        background="rgba(99, 102, 241, 0.08)",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        color="#818cf8",
                        margin_bottom="24px",
                    ),
                    rx.heading("No projects yet", size="5", color="#e4e4e7", font_weight="700", margin_bottom="12px"),
                    rx.text("Create your first project to start uploading research documents and asking questions.",
                            color="#71717a", font_size="0.92rem", text_align="center", max_width="380px", margin_bottom="28px"),
                    rx.button(
                        rx.icon("plus", size=14),
                        rx.text("Create Project"),
                        background_color="rgba(255, 255, 255, 0.03)",
                        border="1px solid rgba(255, 255, 255, 0.08)",
                        color="#e4e4e7",
                        padding="10px 20px",
                        border_radius="10px",
                        font_size="0.88rem",
                        font_weight="600",
                        cursor="pointer",
                        _hover={"background_color": "rgba(255, 255, 255, 0.08)", "border_color": "rgba(99, 102, 241, 0.4)", "color": "white"},
                        on_click=DashboardState.open_modal,
                    ),
                    padding="96px 20px",
                    background="rgba(24, 24, 27, 0.15)",
                    border="1px dashed rgba(255, 255, 255, 0.08)",
                    border_radius="24px",
                    width="100%",
                    align="center",
                ),
            ),
            
            width="100%",
            max_width="1100px",
            margin="0 auto",
            padding="48px 40px",
            z_index="1",
        ),
        
        # New Project Dialog Modal
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title("New Project", font_size="1.4rem", font_weight="800", color="#f4f4f5", margin_bottom="20px"),
                rx.input(
                    placeholder="e.g. MyBombayFilm",
                    max_length=80,
                    value=DashboardState.new_project_name,
                    on_change=DashboardState.set_new_project_name,
                    background="rgba(255, 255, 255, 0.03)",
                    border="1px solid rgba(255, 255, 255, 0.08)",
                    border_radius="12px",
                    padding="14px 18px",
                    color="#f4f4f5",
                    font_size="0.95rem",
                    width="100%",
                    _focus={"border_color": "rgba(99, 102, 241, 0.5)", "background": "rgba(255, 255, 255, 0.05)"}
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancel", background_color="rgba(255, 255, 255, 0.03)", border="1px solid rgba(255, 255, 255, 0.08)", color="#cbd5e1", border_radius="10px", padding="10px 20px", cursor="pointer", _hover={"background_color": "rgba(255, 255, 255, 0.08)", "color": "white"})
                    ),
                    rx.button(
                        "Create",
                        background="linear-gradient(135deg, #6366f1, #4f46e5)",
                        color="white",
                        border_radius="10px",
                        padding="10px 20px",
                        font_weight="700",
                        cursor="pointer",
                        box_shadow="0 4px 10px rgba(99, 102, 241, 0.2)",
                        _hover={"box_shadow": "0 6px 16px rgba(99, 102, 241, 0.4)", "opacity": "0.95"},
                        on_click=DashboardState.create_project,
                    ),
                    spacing="3",
                    margin_top="28px",
                    justify="end",
                ),
                background_color="#18181b",
                border="1px solid rgba(255, 255, 255, 0.08)",
                border_radius="24px",
                padding="36px",
                max_width="420px",
            ),
            open=DashboardState.is_modal_open,
            on_open_change=lambda open: DashboardState.set_is_modal_open(open),
        ),
        
        style=body_style,
        on_mount=DashboardState.load_projects,
    )

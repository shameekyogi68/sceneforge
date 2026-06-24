import reflex as rx
from typing import Any, cast
from sceneforge.state import DashboardState
from sceneforge.styles import GLOBAL_CSS

DASH_KEYFRAMES = """
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
@keyframes cardEntrance {
  from { opacity: 0; transform: translateY(20px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes orbFloat {
  0%, 100% { transform: translate(0,0) scale(1); }
  50%       { transform: translate(20px, -30px) scale(1.04); }
}
@keyframes orbFloat2 {
  0%, 100% { transform: translate(0,0) scale(1); }
  50%       { transform: translate(-25px, 20px) scale(1.06); }
}
@keyframes skeletonShimmer {
  0%, 100% { opacity: 0.2; }
  50%       { opacity: 0.5; }
}
"""

body_style = {
    "font_family": "'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif",
    "background_color": "transparent",
    "min_height": "100vh",
    "color": "#E2E8F0",
    "position": "relative",
    "overflow_x": "hidden",
}


def header_bar() -> rx.Component:
    return rx.hstack(
        # Wordmark
        rx.link(
            rx.hstack(
                rx.text(
                    "tselaf",
                    font_size="1.2rem",
                    font_family="'JetBrains Mono', monospace",
                    font_weight="800",
                    color="#00F0FF",
                    letter_spacing="0.05em",
                    style={
                        "text_shadow": "0 0 10px rgba(0,240,255,0.5)",
                    },
                ),
                align="center",
                spacing="2",
            ),
            href="/dashboard",
            text_decoration="none",
        ),

        # Right side
        rx.hstack(
            # Avatar + email
            rx.hstack(
                rx.box(
                    rx.text(
                        DashboardState.user_avatar_char,
                        font_weight="700",
                        font_size="0.82rem",
                        color="#05080F",
                        text_transform="uppercase",
                    ),
                    width="34px",
                    height="34px",
                    border_radius="50%",
                    background="#00F0FF",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    box_shadow="0 0 10px rgba(0,240,255,0.4)",
                    flex_shrink="0",
                ),
                rx.text(
                    DashboardState.user_email,
                    font_size="0.82rem",
                    color="rgba(255,255,255,0.6)",
                    font_family="'JetBrains Mono', monospace",
                    display=rx.breakpoints(initial="none", sm="block"),
                ),
                align="center",
                spacing="3",
            ),
            # Sign out
            rx.button(
                rx.html("""<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>"""),
                rx.text("TERMINATE", class_name="hud-text", display=rx.breakpoints(initial="none", sm="block")),
                background="transparent",
                border="1px solid rgba(239,68,68,0.4)",
                color="#ef4444",
                border_radius="4px",
                padding="8px 14px",
                font_size="0.75rem",
                cursor="pointer",
                gap="6px",
                transition="all 0.2s ease",
                _hover={
                    "background": "rgba(239,68,68,0.1)",
                    "box_shadow": "0 0 10px rgba(239,68,68,0.3)",
                },
                on_click=cast(Any, DashboardState.logout),
            ),
            align="center",
            spacing="4",
            margin_left="auto",
        ),

        width="100%",
        padding="14px 40px",
        background="rgba(5,8,15,0.8)",
        backdrop_filter="blur(12px)",
        border_bottom="1px solid rgba(0,240,255,0.2)",
        position="sticky",
        top="0",
        z_index="50",
    )


def render_project_card(proj: Any) -> rx.Component:
    return rx.box(
        # Delete button
        rx.button(
            rx.html("""<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>"""),
            position="absolute",
            top="18px",
            right="18px",
            background="transparent",
            border="1px solid rgba(239,68,68,0.3)",
            color="#ef4444",
            border_radius="4px",
            padding="7px",
            cursor="pointer",
            z_index="2",
            transition="all 0.2s ease",
            _hover={
                "background": "rgba(239,68,68,0.15)",
                "box_shadow": "0 0 10px rgba(239,68,68,0.4)",
            },
            on_click=cast(Any, lambda: cast(Any, DashboardState).confirm_delete_project(proj["id"], proj["name"])),
        ),

        # Card content
        rx.vstack(
            rx.box(
                rx.text(f"ID: {proj['id'][:8]}", class_name="hud-text", font_size="0.65rem", color="rgba(0,240,255,0.5)"),
                margin_bottom="4px",
            ),
            rx.text(
                proj["name"],
                font_size="1.1rem",
                font_weight="700",
                color="#E2E8F0",
                word_break="break-all",
                line_height="1.3",
            ),
            # Metadata
            rx.box(
                rx.hstack(
                    rx.text("DOC_COUNT:", class_name="hud-text", font_size="0.65rem", color="rgba(255,255,255,0.4)"),
                    rx.text(proj["document_count"].to(str), class_name="hud-text", font_size="0.65rem", color="#00F0FF"),
                    align="center",
                    spacing="2",
                ),
                rx.hstack(
                    rx.text("CREATED:", class_name="hud-text", font_size="0.65rem", color="rgba(255,255,255,0.4)"),
                    rx.text(proj["created_date"], class_name="hud-text", font_size="0.65rem", color="rgba(255,255,255,0.6)"),
                    align="center",
                    spacing="2",
                ),
                margin_top="12px",
            ),
            spacing="1",
            align_items="start",
        ),

        # Styling
        class_name="glass-panel",
        padding="24px",
        cursor="pointer",
        position="relative",
        transition="all 0.2s ease",
        _hover={
            "transform": "translateY(-3px)",
            "border_color": "rgba(0,240,255,0.4)",
            "box_shadow": "0 8px 32px rgba(0,240,255,0.1)",
        },
        on_click=cast(Any, lambda: rx.redirect(f"/project?project_id={proj['id']}")),
        style={"animation": "cardEntrance 0.4s ease both"},
    )


def project_skeleton_card() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.box(
                width="40%", height="10px",
                background="rgba(0,240,255,0.1)",
                style={"animation": "skeletonShimmer 1.5s infinite linear"},
            ),
            rx.box(
                width="80%", height="18px",
                background="rgba(255,255,255,0.05)",
                style={"animation": "skeletonShimmer 1.5s infinite linear 0.2s"},
            ),
            rx.box(
                width="60%", height="10px",
                background="rgba(255,255,255,0.03)",
                style={"animation": "skeletonShimmer 1.5s infinite linear 0.4s"},
            ),
            spacing="3",
            align_items="start",
        ),
        class_name="glass-panel",
        padding="24px",
    )


def dashboard_page() -> rx.Component:
    return rx.box(
        rx.html(f"<style>{GLOBAL_CSS}{DASH_KEYFRAMES}</style>"),
        rx.cond(DashboardState.is_loading, rx.box(
            width="100%", height="2px",
            background="linear-gradient(90deg, #00F0FF 0%, #8B5CF6 50%, #00F0FF 100%)",
            background_size="200% 100%", position="absolute", top="0", left="0", z_index="1000",
            style={"animation": "pulseNeon 1.5s linear infinite"}
        ), rx.fragment()),

        header_bar(),

        # Ambient background touches
        rx.box(
            width="600px", height="600px",
            background="radial-gradient(circle, rgba(0,240,255,0.05), transparent 70%)",
            position="absolute", border_radius="50%", filter="blur(80px)",
            top="-20%", left="-10%", z_index="0", pointer_events="none",
        ),
        rx.box(
            width="500px", height="500px",
            background="radial-gradient(circle, rgba(139,92,246,0.05), transparent 70%)",
            position="absolute", border_radius="50%", filter="blur(80px)",
            bottom="-10%", right="-10%", z_index="0", pointer_events="none",
        ),

        # Main content
        rx.vstack(
            # Header
            rx.vstack(
                rx.text("SYSTEM ACCESS // DIRECTORIES", class_name="hud-text", font_size="0.8rem", color="rgba(0,240,255,0.6)"),
                rx.heading("Active Projects", size="7", font_weight="800", color="#E2E8F0"),
                spacing="2",
                align_items="start",
                style={"animation": "fadeSlideUp 0.4s ease 0.1s both"},
            ),

            # Toolbar
            rx.hstack(
                rx.hstack(
                    rx.html("""<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#00F0FF" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>"""),
                    rx.input(
                        placeholder="SEARCH_INDEX...",
                        value=DashboardState.search_query,
                        on_change=cast(Any, DashboardState.set_search_query),
                        border="none", outline="none", background="transparent",
                        color="#E2E8F0", font_family="'JetBrains Mono', monospace", font_size="0.85rem",
                        width="100%", style={"caret-color": "#00F0FF"},
                        _placeholder={"color": "rgba(255,255,255,0.3)"},
                    ),
                    class_name="premium-input",
                    border_radius="4px", padding="8px 12px", width="100%", max_width="320px", align_items="center", gap="8px",
                ),
                rx.button(
                    rx.text("+ INIT_PROJECT", class_name="hud-text", font_size="0.8rem"),
                    background="transparent",
                    color="#00F0FF",
                    border="1px solid #00F0FF",
                    border_radius="4px",
                    padding="10px 16px",
                    cursor="pointer",
                    class_name="cyber-button-hover",
                    on_click=cast(Any, DashboardState.open_modal),
                ),
                width="100%", justify="between", align_items="center",
                style={"animation": "fadeSlideUp 0.4s ease 0.2s both"},
            ),

            # Grid
            rx.cond(
                DashboardState.is_loading,
                rx.grid(
                    project_skeleton_card(), project_skeleton_card(), project_skeleton_card(),
                    columns=rx.breakpoints(initial="1", sm="2", md="3"), spacing="5", width="100%",
                ),
                rx.cond(
                    cast(Any, DashboardState.filtered_projects).length() > 0,
                    rx.grid(
                        rx.foreach(cast(Any, DashboardState.filtered_projects).to(list[dict[str, Any]]), render_project_card),
                        columns=rx.breakpoints(initial="1", sm="2", md="3"), spacing="5", width="100%",
                        style={"animation": "fadeIn 0.3s ease 0.3s both"},
                    ),
                    rx.vstack(
                        rx.box(
                            rx.text("NO_DATA_FOUND", class_name="hud-text", font_size="1rem", color="rgba(255,255,255,0.4)"),
                            margin_bottom="16px",
                        ),
                        rx.button(
                            rx.text("+ INIT_FIRST_PROJECT", class_name="hud-text", font_size="0.8rem"),
                            background="rgba(0,240,255,0.1)", color="#00F0FF", border="1px solid #00F0FF",
                            border_radius="4px", padding="10px 16px", cursor="pointer", class_name="cyber-button-hover",
                            on_click=cast(Any, DashboardState.open_modal),
                        ),
                        class_name="glass-panel", padding="60px 24px", width="100%", align="center",
                        style={"animation": "fadeSlideUp 0.4s ease 0.3s both"},
                    ),
                ),
            ),
            width="100%", max_width="1100px", margin="0 auto", padding="48px 40px", z_index="1", spacing="6", class_name="page-transition",
        ),

        # Modals
        rx.dialog.root(
            rx.dialog.content(
                rx.vstack(
                    rx.text("SYSTEM_COMMAND // NEW_PROJECT", class_name="hud-text", font_size="0.75rem", color="rgba(0,240,255,0.6)"),
                    rx.heading("Initialize Directory", size="6", font_weight="800", color="#E2E8F0"),
                    margin_bottom="20px", spacing="1", align_items="start",
                ),
                rx.input(
                    placeholder="ENTER_DIRECTORY_NAME...", max_length=80,
                    value=DashboardState.new_project_name, on_change=cast(Any, DashboardState.set_new_project_name),
                    class_name="premium-input", border_radius="4px", padding="12px 16px", width="100%", margin_bottom="24px",
                ),
                rx.hstack(
                    rx.dialog.close(rx.button("CANCEL", class_name="hud-text", font_size="0.75rem", background="transparent", border="1px solid rgba(255,255,255,0.2)", color="rgba(255,255,255,0.6)", padding="8px 16px", border_radius="4px", cursor="pointer")),
                    rx.button("EXECUTE", class_name="hud-text", font_size="0.75rem", background="transparent", border="1px solid #00F0FF", color="#00F0FF", padding="8px 16px", border_radius="4px", cursor="pointer", _hover={"box_shadow": "0 0 10px rgba(0,240,255,0.4)"}, on_click=cast(Any, DashboardState.create_project)),
                    spacing="3", justify="end",
                ),
                class_name="glass-panel", padding="32px", max_width="400px",
            ),
            open=DashboardState.is_modal_open, on_open_change=cast(Any, DashboardState.set_is_modal_open),
        ),

        rx.dialog.root(
            rx.dialog.content(
                rx.vstack(
                    rx.text("WARNING // DESTRUCTIVE_ACTION", class_name="hud-text", font_size="0.75rem", color="#ef4444"),
                    rx.heading("Delete Directory?", size="6", font_weight="800", color="#E2E8F0"),
                    rx.text(f"Confirm deletion of '{DashboardState.project_to_delete_name}'. All data will be purged.", font_size="0.85rem", color="rgba(255,255,255,0.6)", margin_top="8px"),
                    margin_bottom="24px", spacing="1", align_items="start",
                ),
                rx.hstack(
                    rx.button("ABORT", class_name="hud-text", font_size="0.75rem", background="transparent", border="1px solid rgba(255,255,255,0.2)", color="rgba(255,255,255,0.6)", padding="8px 16px", border_radius="4px", cursor="pointer", on_click=cast(Any, DashboardState.close_delete_confirm)),
                    rx.button("CONFIRM_PURGE", class_name="hud-text", font_size="0.75rem", background="transparent", border="1px solid #ef4444", color="#ef4444", padding="8px 16px", border_radius="4px", cursor="pointer", _hover={"box_shadow": "0 0 10px rgba(239,68,68,0.4)"}, on_click=cast(Any, DashboardState.execute_delete_project)),
                    spacing="3", justify="end",
                ),
                class_name="glass-panel", padding="32px", max_width="400px", border="1px solid rgba(239,68,68,0.3)",
            ),
            open=DashboardState.is_delete_confirm_open, on_open_change=cast(Any, DashboardState.set_is_delete_confirm_open),
        ),

        style=body_style,
        on_mount=cast(Any, DashboardState.load_projects),
    )

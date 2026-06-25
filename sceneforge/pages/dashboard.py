import reflex as rx
from typing import Any, cast
from sceneforge.state import DashboardState
from sceneforge.styles import GLOBAL_CSS
from sceneforge.pages.navigation import sidebar_nav

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
@keyframes statusPulse {
  0%,100% { opacity: 1; }
  50%      { opacity: 0.5; }
}
"""

body_style = {
    "font_family": "'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif",
    "background_color": "#05080F",
    "height": "100vh",
    "width": "100vw",
    "color": "#E2E8F0",
    "overflow": "hidden",
    "display": "flex",
}

def render_project_card(proj: Any) -> rx.Component:
    return rx.box(
        # Delete button
        rx.button(
            rx.html("""<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>"""),
            position="absolute",
            top="18px",
            right="18px",
            background="transparent",
            border="none",
            color="rgba(255,255,255,0.4)",
            border_radius="4px",
            padding="7px",
            cursor="pointer",
            z_index="10",
            transition="all 0.2s ease",
            _hover={
                "color": "#ef4444",
                "background": "rgba(239,68,68,0.1)",
            },
            on_click=cast(Any, lambda: cast(Any, DashboardState).confirm_delete_project(proj.id, proj.name)),
        ),

        # Card content
        rx.vstack(
            # Folder icon glowing box
            rx.box(
                rx.html("""<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00F0FF" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>"""),
                width="40px",
                height="40px",
                border_radius="10px",
                background="rgba(0, 240, 255, 0.08)",
                border="1px solid rgba(0, 240, 255, 0.2)",
                display="flex",
                align_items="center",
                justify_content="center",
                margin_bottom="12px",
            ),
            rx.text(
                proj.name,
                font_size="1.1rem",
                font_weight="700",
                color="#E2E8F0",
                word_break="break-all",
                line_height="1.3",
            ),
            # Metadata
            rx.vstack(
                rx.hstack(
                    rx.html("""<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.4)" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>"""),
                    rx.text(proj.document_count.to(str) + " DOCUMENT" + rx.cond(proj.document_count == 1, "", "S"), class_name="hud-text", font_size="0.65rem", color="rgba(255,255,255,0.4)"),
                    align="center",
                    spacing="2",
                ),
                rx.hstack(
                    rx.html("""<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.4)" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>"""),
                    rx.text("MODIFIED: " + proj.created_date, class_name="hud-text", font_size="0.65rem", color="rgba(255,255,255,0.4)"),
                    align="center",
                    spacing="2",
                ),
                margin_top="12px",
                spacing="2",
                align_items="start",
            ),
            spacing="1",
            align_items="start",
        ),

        # Styling
        class_name="glass-panel",
        padding="24px",
        cursor="pointer",
        position="relative",
        transition="all 0.25s cubic-bezier(0.16,1,0.3,1)",
        _hover={
            "transform": "translateY(-4px)",
            "border_color": "rgba(0,240,255,0.35)",
            "box_shadow": "0 12px 32px rgba(0,240,255,0.1), inset 0 0 10px rgba(0,240,255,0.05)",
        },
        on_click=cast(Any, lambda: cast(Any, DashboardState).go_to_project(proj.id)),
        style={"animation": "cardEntrance 0.4s ease both"},
    )

def project_skeleton_card() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.box(
                width="40px", height="40px",
                border_radius="10px",
                background="rgba(0,240,255,0.08)",
                style={"animation": "statusPulse 1.5s infinite"},
                margin_bottom="12px",
            ),
            rx.box(
                width="80%", height="18px",
                background="rgba(255,255,255,0.05)",
                style={"animation": "statusPulse 1.5s infinite 0.2s"},
            ),
            rx.box(
                width="60%", height="10px",
                background="rgba(255,255,255,0.03)",
                style={"animation": "statusPulse 1.5s infinite 0.4s"},
            ),
            spacing="3",
            align_items="start",
        ),
        class_name="glass-panel",
        padding="24px",
    )

def stats_widget_card(title: str, subtitle: str, value: str, footer_comp: rx.Component, icon_svg: str) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(title, class_name="hud-text", font_size="0.7rem", color="rgba(0,240,255,0.75)", font_weight="700"),
                rx.text(subtitle, font_size="0.8rem", color="rgba(255,255,255,0.45)"),
                rx.heading(value, size="8", font_weight="800", color="#fff", margin_top="12px", letter_spacing="-0.02em"),
                footer_comp,
                align_items="start",
                spacing="1",
            ),
            rx.spacer(),
            rx.center(
                rx.html(icon_svg),
                width="48px",
                height="48px",
                border_radius="10px",
                background="rgba(0, 240, 255, 0.04)",
                border="1px solid rgba(0, 240, 255, 0.1)",
            ),
            align_items="start",
            width="100%",
        ),
        class_name="glass-panel-glow",
        padding="24px",
    )

def dashboard_page() -> rx.Component:
    # Dashboard Content
    main_dashboard_content = rx.vstack(
        # Top Header
        rx.hstack(
            rx.vstack(
                rx.hstack(
                    rx.box(width="6px", height="6px", border_radius="50%", background_color="#00F0FF", style={"animation": "statusPulse 1.2s infinite"}),
                    rx.text("PROJECTS_LIBRARY", class_name="hud-text", font_size="0.65rem", color="rgba(0,240,255,0.7)"),
                    align="center",
                    spacing="2",
                ),
                rx.heading("ScriptIQ Writer Studio", size="6", font_weight="800", color="#fff", letter_spacing="-0.01em"),
                spacing="1",
                align_items="start",
            ),
            rx.spacer(),
            # Search Bar input
            rx.hstack(
                rx.html("""<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#00F0FF" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>"""),
                rx.input(
                    placeholder="Search projects or documents...",
                    value=DashboardState.search_query,
                    on_change=cast(Any, DashboardState.set_search_query),
                    border="none", outline="none", background="transparent",
                    color="#E2E8F0", font_family="'Plus Jakarta Sans', sans-serif", font_size="0.82rem",
                    width="100%", style={"caret-color": "#00F0FF"},
                    _placeholder={"color": "rgba(255,255,255,0.3)"},
                ),
                class_name="premium-input",
                border_radius="100px", padding="8px 16px", width="260px", align_items="center", gap="8px",
            ),
            # Latency Indicator
            rx.box(
                rx.hstack(
                    rx.html("""<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#00F0FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 19A3.5 3.5 0 0 0 21 15.5c0-2.79-2.54-4.5-5-4.5-.42-1.02-1.39-2.5-3-2.5a5 5 0 0 0-5 5c0 .64.11 1.26.31 1.83A3.25 3.25 0 0 0 5 19.5h12.5z"/></svg>"""),
                    rx.text("CLOUD_SYNC: AUTO", class_name="hud-text", font_size="0.65rem", color="rgba(0,240,255,0.85)"),
                    align="center",
                    spacing="2",
                ),
                background="rgba(0, 240, 255, 0.08)",
                border="1px solid rgba(0, 240, 255, 0.2)",
                border_radius="100px",
                padding="8px 16px",
            ),
            # New Project Action Pill
            rx.button(
                rx.text("+ New Project", font_size="0.82rem", font_weight="700"),
                background="linear-gradient(135deg, #00F0FF 0%, #0072FF 100%)",
                color="#05080F",
                border_radius="100px",
                padding="10px 22px",
                cursor="pointer",
                box_shadow="0 0 15px rgba(0, 240, 255, 0.25)",
                transition="all 0.2s ease",
                _hover={
                    "box_shadow": "0 0 25px rgba(0, 240, 255, 0.45)",
                },
                on_click=cast(Any, DashboardState.open_modal),
            ),
            width="100%",
            align_items="center",
            spacing="4",
            padding_bottom="12px",
        ),

        # Horizontal Divider line
        rx.box(width="100%", height="1px", background="rgba(255,255,255,0.06)", margin_y="4px"),

        # Section Header
        rx.vstack(
            rx.heading("Your Writing Projects", size="5", font_weight="800", color="#fff", margin_top="16px"),
            rx.text("Each project holds its own research documents, reference files, and AI chat history.", color="rgba(255,255,255,0.45)", font_size="0.85rem"),
            spacing="1",
            align_items="start",
        ),

        # Projects Grid
        rx.cond(
            DashboardState.is_loading,
            rx.grid(
                project_skeleton_card(), project_skeleton_card(), project_skeleton_card(),
                columns=rx.breakpoints(initial="1", sm="2", md="3"), spacing="5", width="100%",
            ),
            rx.cond(
                cast(Any, DashboardState.filtered_projects).length() > 0,
                rx.grid(
                    rx.foreach(DashboardState.filtered_projects, render_project_card),
                    # NEW SEQUENCE block
                    rx.vstack(
                        rx.box(
                            rx.html("""<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="rgba(0,240,255,0.6)" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>"""),
                            width="44px",
                            height="44px",
                            border_radius="50%",
                            border="1px solid rgba(0, 240, 255, 0.3)",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                        ),
                        rx.text("NEW WRITING PROJECT", class_name="hud-text", font_size="0.75rem", color="rgba(0,240,255,0.6)"),
                        spacing="3",
                        align_items="center",
                        justify_content="center",
                        height="100%",
                        min_height="180px",
                        border="1px dashed rgba(0, 240, 255, 0.25)",
                        border_radius="16px",
                        padding="32px",
                        cursor="pointer",
                        _hover={
                            "border_color": "#00F0FF",
                            "background": "rgba(0,240,255,0.02)",
                            "box_shadow": "0 0 15px rgba(0,240,255,0.08)",
                        },
                        on_click=cast(Any, DashboardState.open_modal),
                    ),
                    columns=rx.breakpoints(initial="1", sm="2", md="3"), spacing="5", width="100%",
                    style={"animation": "fadeIn 0.3s ease 0.3s both"},
                ),
                rx.vstack(
                    rx.box(
                        rx.text("NO PROJECTS FOUND", class_name="hud-text", font_size="1rem", color="rgba(255,255,255,0.4)"),
                        margin_bottom="16px",
                    ),
                    rx.button(
                        rx.text("Start your first writing project", class_name="hud-text", font_size="0.8rem"),
                        background="rgba(0,240,255,0.1)", color="#00F0FF", border="1px solid #00F0FF",
                        border_radius="4px", padding="10px 16px", cursor="pointer", class_name="cyber-button-hover",
                        on_click=cast(Any, DashboardState.open_modal),
                    ),
                    class_name="glass-panel", padding="60px 24px", width="100%", align="center",
                    style={"animation": "fadeSlideUp 0.4s ease 0.3s both"},
                ),
            ),
        ),

        width="100%",
        height="100vh",
        overflow_y="auto",
        padding="40px",
        spacing="6",
        z_index="1",
        class_name="page-transition",
    )

    return rx.box(
        rx.html(f"<style>{GLOBAL_CSS}{DASH_KEYFRAMES}</style>"),
        rx.cond(DashboardState.is_loading, rx.box(
            width="100%", height="2px",
            background_color="#00F0FF",
            background="linear-gradient(90deg, #00F0FF 0%, #00B8FF 50%, #00F0FF 100%)",
            background_size="200% 100%", position="absolute", top="0", left="0", z_index="1000",
            style={"animation": "progressGlow 1.5s linear infinite"},
            box_shadow="0 0 10px #00F0FF, 0 0 4px #00B8FF",
        ), rx.fragment()),

        # Layout wrapper
        rx.hstack(
            sidebar_nav("dashboard", DashboardState.user_avatar_char, DashboardState.user_email, DashboardState.logout),
            main_dashboard_content,
            width="100%",
            height="100vh",
            align_items="start",
            spacing="0",
        ),

        # Modals
        rx.dialog.root(
            rx.dialog.content(
                # Modal header bar
                rx.box(
                    rx.hstack(
                        rx.hstack(
                            rx.box(width="5px", height="5px", border_radius="50%", background_color="#00F0FF", style={"animation": "statusPulse 1.2s infinite"}),
                            rx.text("NEW PROJECT", class_name="hud-text", font_size="0.6rem", color="#00F0FF"),
                            align="center", spacing="2",
                        ),
                        rx.spacer(),
                        rx.text("ScriptIQ v4.0", class_name="hud-text", font_size="0.6rem", color="rgba(255,255,255,0.3)"),
                        align="center", spacing="2",
                    ),
                    border_bottom="1px solid rgba(255,255,255,0.06)",
                    padding_bottom="12px",
                    margin_bottom="20px",
                    width="100%",
                ),
                
                # Title
                rx.vstack(
                    rx.heading("Create Writing Project", size="6", font_weight="800", color="#E2E8F0"),
                    rx.text("Set up a new workspace for your reference and research documents.", font_size="0.8rem", color="rgba(255,255,255,0.45)"),
                    margin_bottom="20px", spacing="1", align_items="start",
                ),

                # Input Section
                rx.vstack(
                    rx.hstack(
                        rx.text("PROJECT TITLE", class_name="hud-text", font_size="0.68rem", color="#00F0FF", font_weight="700"),
                        width="100%",
                    ),
                    rx.input(
                        placeholder="e.g. Project Astra", max_length=80,
                        value=DashboardState.new_project_name, on_change=cast(Any, DashboardState.set_new_project_name),
                        class_name="premium-input", border_radius="6px", padding="12px 16px", width="100%",
                    ),
                    align_items="start",
                    spacing="2",
                    width="100%",
                    margin_bottom="18px",
                ),

                # Genre Tags Section
                rx.vstack(
                    rx.text("PROJECT GENRE / CATEGORY", class_name="hud-text", font_size="0.68rem", color="#00F0FF", font_weight="700"),
                    rx.hstack(
                        rx.box(rx.text("DRAMA", font_size="0.75rem", font_weight="700", color="#05080F"), background_color="#00F0FF", border_radius="6px", padding="5px 12px", cursor="pointer"),
                        rx.box(rx.text("THRILLER", font_size="0.75rem", font_weight="600", color="rgba(255,255,255,0.6)"), border="1px solid rgba(255,255,255,0.12)", border_radius="6px", padding="5px 12px", cursor="pointer"),
                        rx.box(rx.text("COMEDY", font_size="0.75rem", font_weight="600", color="rgba(255,255,255,0.6)"), border="1px solid rgba(255,255,255,0.12)", border_radius="6px", padding="5px 12px", cursor="pointer"),
                        rx.box(rx.text("SCI-FI", font_size="0.75rem", font_weight="600", color="rgba(255,255,255,0.6)"), border="1px solid rgba(255,255,255,0.12)", border_radius="6px", padding="5px 12px", cursor="pointer"),
                        rx.box(rx.text("+ ADD", font_size="0.75rem", font_weight="600", color="rgba(0,240,255,0.5)"), border="1px dashed rgba(0,240,255,0.3)", border_radius="6px", padding="5px 12px", cursor="pointer"),
                        spacing="2",
                        wrap="wrap",
                    ),
                    align_items="start",
                    spacing="2",
                    width="100%",
                    margin_bottom="18px",
                ),

                # Upload Placeholder Section
                rx.vstack(
                    rx.text("UPLOAD RESEARCH / REFERENCE (.PDF)", class_name="hud-text", font_size="0.68rem", color="#00F0FF", font_weight="700"),
                    rx.vstack(
                        rx.box(
                            rx.html("""<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00F0FF" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="15" x2="23" y2="15"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="15" x2="4" y2="15"/></svg>"""),
                            width="38px",
                            height="38px",
                            border_radius="50%",
                            background="rgba(0,240,255,0.08)",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                            box_shadow="0 0 10px rgba(0,240,255,0.3)",
                        ),
                        rx.text("Drag research PDF here", font_size="0.82rem", font_weight="700", color="#fff"),
                        rx.text("or click to select file from device. Max 50MB.", font_size="0.75rem", color="rgba(255,255,255,0.4)"),
                        spacing="2",
                        align_items="center",
                        justify_content="center",
                        width="100%",
                        padding="24px",
                        border="1px dashed rgba(0, 240, 255, 0.2)",
                        border_radius="10px",
                        background="rgba(0, 240, 255, 0.01)",
                    ),
                    align_items="start",
                    spacing="2",
                    width="100%",
                    margin_bottom="24px",
                ),

                # Bottom action buttons
                rx.hstack(
                    rx.spacer(),
                    rx.button("CANCEL", class_name="hud-text", font_size="0.72rem", background="transparent", border="none", color="rgba(255,255,255,0.45)", padding="8px 16px", cursor="pointer", _hover={"color": "#fff"}, on_click=cast(Any, DashboardState.close_modal)),
                    rx.button(
                        rx.hstack(
                            rx.text("CREATE PROJECT", class_name="hud-text", font_size="0.75rem", font_weight="700"),
                            rx.html("""<svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>"""),
                            align="center", spacing="2",
                        ),
                        background="#00F0FF",
                        color="#05080F",
                        padding="10px 20px",
                        border_radius="8px",
                        cursor="pointer",
                        box_shadow="0 0 15px rgba(0, 240, 255, 0.4)",
                        _hover={"box_shadow": "0 0 25px rgba(0, 240, 255, 0.6)"},
                        on_click=cast(Any, DashboardState.create_project)
                    ),
                    spacing="4",
                    width="100%",
                    align_items="center",
                ),
                
                class_name="glass-panel-glow", padding="28px", max_width="480px",
            ),
            open=DashboardState.is_modal_open, on_open_change=cast(Any, DashboardState.set_is_modal_open),
        ),

        rx.dialog.root(
            rx.dialog.content(
                rx.vstack(
                    rx.text("DELETE PROJECT", class_name="hud-text", font_size="0.75rem", color="#ef4444"),
                    rx.heading("Delete Writing Project?", size="6", font_weight="800", color="#E2E8F0"),
                    rx.text(f"Confirm deletion of '{DashboardState.project_to_delete_name}'. This project's research, files and chat history will be permanently deleted.", font_size="0.85rem", color="rgba(255,255,255,0.6)", margin_top="8px"),
                    margin_bottom="24px", spacing="1", align_items="start",
                ),
                rx.hstack(
                    rx.button("CANCEL", class_name="hud-text", font_size="0.75rem", background="transparent", border="1px solid rgba(255,255,255,0.2)", color="rgba(255,255,255,0.6)", padding="8px 16px", border_radius="4px", cursor="pointer", on_click=cast(Any, DashboardState.close_delete_confirm)),
                    rx.button("DELETE PERMANENTLY", class_name="hud-text", font_size="0.75rem", background="transparent", border="1px solid #ef4444", color="#ef4444", padding="8px 16px", border_radius="4px", cursor="pointer", _hover={"box_shadow": "0 0 10px rgba(239,68,68,0.4)"}, on_click=cast(Any, DashboardState.execute_delete_project)),
                    spacing="3", justify="end",
                ),
                class_name="glass-panel", padding="32px", max_width="400px", border="1px solid rgba(239,68,68,0.3)",
            ),
            open=DashboardState.is_delete_confirm_open, on_open_change=cast(Any, DashboardState.set_is_delete_confirm_open),
        ),

        style=body_style,
        on_mount=cast(Any, DashboardState.load_projects),
    )

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
@keyframes shimmerText {
  0%   { background-position: -200% center; }
  100% { background-position:  200% center; }
}
@keyframes orbFloat {
  0%, 100% { transform: translate(0,0) scale(1); }
  50%       { transform: translate(20px, -30px) scale(1.04); }
}
@keyframes orbFloat2 {
  0%, 100% { transform: translate(0,0) scale(1); }
  50%       { transform: translate(-25px, 20px) scale(1.06); }
}
@keyframes spinnerPulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.5; }
}
@keyframes deletePop {
  0%   { transform: scale(1); }
  40%  { transform: scale(1.15); }
  100% { transform: scale(1); }
}
@keyframes skeletonShimmer {
  0%, 100% { opacity: 0.35; }
  50%       { opacity: 0.7; }
}
"""

body_style = {
    "font_family": "'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif",
    "background_color": "#080810",
    "min_height": "100vh",
    "color": "#f4f4f5",
    "position": "relative",
    "overflow_x": "hidden",
}


def header_bar() -> rx.Component:
    return rx.hstack(
        # Logo
        rx.link(
            rx.hstack(
                rx.box(
                    rx.html("""<svg style="width:20px;height:20px;color:#a5b4fc;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20.2 6 3 11l-.9-2.4 17.2-5.1Z"/>
                        <path d="M2 12V4a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-4"/>
                        <path d="M2 12h20"/>
                        <path d="m7 2 2 4"/><path d="m12 2 2 4"/><path d="m17 2 2 4"/>
                    </svg>"""),
                    width="36px",
                    height="36px",
                    border_radius="10px",
                    background="linear-gradient(135deg, rgba(99,102,241,0.2), rgba(168,85,247,0.15))",
                    border="1px solid rgba(99,102,241,0.25)",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    box_shadow="0 0 20px rgba(99,102,241,0.15)",
                ),
                rx.text(
                    "SceneForge",
                    font_size="1.2rem",
                    font_weight="800",
                    letter_spacing="-0.03em",
                    style={
                        "background": "linear-gradient(135deg, #c7d2fe 0%, #a5b4fc 50%, #c084fc 100%)",
                        "background_size": "200% auto",
                        "-webkit-background-clip": "text",
                        "-webkit-text-fill-color": "transparent",
                        "background-clip": "text",
                        "animation": "shimmerText 4s linear infinite",
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
                        color="white",
                        text_transform="uppercase",
                    ),
                    width="34px",
                    height="34px",
                    border_radius="50%",
                    background="linear-gradient(135deg, #6366f1, #a855f7)",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    box_shadow="0 0 16px rgba(99,102,241,0.35)",
                    flex_shrink="0",
                ),
                rx.text(
                    DashboardState.user_email,
                    font_size="0.82rem",
                    color="rgba(161,161,170,0.8)",
                    font_weight="500",
                    display=rx.breakpoints(initial="none", sm="block"),
                ),
                align="center",
                spacing="2",
            ),
            # Sign out
            rx.button(
                rx.html("""<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>"""),
                rx.text("Sign Out", display=rx.breakpoints(initial="none", sm="block")),
                background="rgba(255,255,255,0.03)",
                border="1px solid rgba(255,255,255,0.08)",
                color="rgba(212,212,216,0.8)",
                border_radius="10px",
                padding="8px 14px",
                font_size="0.82rem",
                font_weight="600",
                cursor="pointer",
                gap="6px",
                transition="all 0.2s ease",
                _hover={
                    "background": "rgba(239,68,68,0.08)",
                    "border_color": "rgba(239,68,68,0.3)",
                    "color": "#fca5a5",
                    "transform": "translateY(-1px)",
                },
                _active={"transform": "translateY(0)"},
                on_click=cast(Any, DashboardState.logout),
            ),
            align="center",
            spacing="3",
            margin_left="auto",
        ),

        width="100%",
        padding="14px 40px",
        background="rgba(8,8,16,0.7)",
        backdrop_filter="blur(28px) saturate(1.5)",
        border_bottom="1px solid rgba(255,255,255,0.06)",
        position="sticky",
        top="0",
        z_index="50",
    )


def render_project_card(proj: Any) -> rx.Component:
    return rx.box(
        # Delete button — top right
        rx.button(
            rx.html("""<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
                <path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
            </svg>"""),
            position="absolute",
            top="18px",
            right="18px",
            background="rgba(239,68,68,0.05)",
            border="1px solid rgba(239,68,68,0.12)",
            color="rgba(252,165,165,0.7)",
            border_radius="8px",
            padding="7px",
            cursor="pointer",
            z_index="2",
            transition="all 0.2s cubic-bezier(0.16,1,0.3,1)",
            _hover={
                "background": "#ef4444",
                "border_color": "#ef4444",
                "color": "#ffffff",
                "transform": "scale(1.1)",
                "box_shadow": "0 4px 12px rgba(239,68,68,0.35)",
            },
            _active={"transform": "scale(0.95)"},
            on_click=cast(Any, lambda: cast(Any, DashboardState).confirm_delete_project(proj["id"], proj["name"])),
        ),

        # Card content
        rx.vstack(
            # Icon
            rx.box(
                rx.html("""<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                </svg>"""),
                width="44px",
                height="44px",
                border_radius="12px",
                background="rgba(99,102,241,0.1)",
                border="1px solid rgba(99,102,241,0.2)",
                color="#818cf8",
                display="flex",
                align_items="center",
                justify_content="center",
                margin_bottom="16px",
                transition="all 0.3s ease",
            ),
            rx.text(
                proj["name"],
                font_size="1.05rem",
                font_weight="700",
                color="#f4f4f5",
                word_break="break-all",
                line_height="1.3",
                letter_spacing="-0.01em",
            ),
            rx.text(
                proj["created_date"],
                font_size="0.77rem",
                color="rgba(113,113,122,0.7)",
                font_weight="500",
            ),
            spacing="1",
            align_items="start",
        ),

        # Gradient line at bottom on hover (via box-shadow trick)
        background="rgba(20,20,28,0.5)",
        border="1px solid rgba(255,255,255,0.055)",
        border_radius="20px",
        padding="28px 26px",
        cursor="pointer",
        position="relative",
        backdrop_filter="blur(16px)",
        overflow="hidden",
        transition="all 0.3s cubic-bezier(0.16,1,0.3,1)",
        _hover={
            "transform": "translateY(-5px)",
            "background": "rgba(99,102,241,0.05)",
            "border_color": "rgba(99,102,241,0.35)",
            "box_shadow": "0 20px 48px -8px rgba(99,102,241,0.12), 0 0 0 1px rgba(99,102,241,0.12)",
        },
        _active={"transform": "translateY(-2px)"},
        on_click=cast(Any, lambda: rx.redirect(f"/project?project_id={proj['id']}")),
        style={"animation": "cardEntrance 0.5s cubic-bezier(0.16,1,0.3,1) both"},
    )


def project_skeleton_card() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.box(
                width="44px",
                height="44px",
                border_radius="12px",
                background="linear-gradient(90deg, rgba(255,255,255,0.03) 25%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0.03) 75%)",
                background_size="200% 100%",
                style={"animation": "skeletonPulse 1.6s infinite linear"},
            ),
            rx.box(
                width="70%",
                height="16px",
                border_radius="4px",
                background="linear-gradient(90deg, rgba(255,255,255,0.02) 25%, rgba(255,255,255,0.06) 50%, rgba(255,255,255,0.02) 75%)",
                background_size="200% 100%",
                style={"animation": "skeletonPulse 1.6s infinite linear 0.2s"},
            ),
            rx.box(
                width="40%",
                height="12px",
                border_radius="4px",
                background="linear-gradient(90deg, rgba(255,255,255,0.01) 25%, rgba(255,255,255,0.04) 50%, rgba(255,255,255,0.01) 75%)",
                background_size="200% 100%",
                style={"animation": "skeletonPulse 1.6s infinite linear 0.4s"},
            ),
            spacing="3",
            align_items="start",
        ),
        background="rgba(20,20,28,0.3)",
        border="1px solid rgba(255,255,255,0.03)",
        border_radius="20px",
        padding="28px 26px",
    )


def loading_bar(is_active: Any) -> rx.Component:
    return rx.cond(
        is_active,
        rx.box(
            width="100%",
            height="3px",
            background="linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #6366f1 100%)",
            background_size="200% 100%",
            position="absolute",
            top="0",
            left="0",
            z_index="1000",
            style={"animation": "progressGlow 1.5s linear infinite"},
        ),
        rx.fragment()
    )


def dashboard_page() -> rx.Component:
    return rx.box(
        rx.html(f"<style>{GLOBAL_CSS}{DASH_KEYFRAMES}</style>"),
        loading_bar(DashboardState.is_loading),

        header_bar(),

        # Ambient orbs
        rx.box(
            width="700px", height="700px",
            background="radial-gradient(circle, rgba(99,102,241,0.5), rgba(79,70,229,0.2))",
            position="absolute", border_radius="50%",
            filter="blur(130px)", opacity="0.07",
            top="-300px", left="-200px", z_index="0",
            pointer_events="none",
            style={"animation": "orbFloat 20s ease-in-out infinite"},
        ),
        rx.box(
            width="600px", height="600px",
            background="radial-gradient(circle, rgba(168,85,247,0.5), rgba(124,58,237,0.2))",
            position="absolute", border_radius="50%",
            filter="blur(130px)", opacity="0.06",
            bottom="-200px", right="-150px", z_index="0",
            pointer_events="none",
            style={"animation": "orbFloat2 24s ease-in-out infinite"},
        ),

        # Main content
        rx.vstack(
            # Page heading
            rx.vstack(
                rx.heading(
                    "Your Projects",
                    size="8",
                    font_weight="800",
                    color="#f4f4f5",
                    letter_spacing="-0.04em",
                    line_height="1.1",
                ),
                rx.text(
                    "Each project holds its own research documents and AI chat history.",
                    color="rgba(161,161,170,0.7)",
                    font_size="0.92rem",
                    letter_spacing="0.005em",
                ),
                spacing="2",
                align_items="start",
                style={"animation": "fadeSlideUp 0.5s cubic-bezier(0.16,1,0.3,1) 0.1s both"},
            ),

            # Toolbar
            rx.hstack(
                # Search
                rx.hstack(
                    rx.html("""<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="rgba(113,113,122,0.8)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>"""),
                    rx.input(
                        placeholder="Search projects...",
                        value=DashboardState.search_query,
                        on_change=cast(Any, DashboardState.set_search_query),
                        border="none",
                        outline="none",
                        color="#f4f4f5",
                        font_size="0.875rem",
                        background="transparent",
                        width="100%",
                        style={"caret-color": "#818cf8"},
                        _placeholder={"color": "rgba(113,113,122,0.6)"},
                    ),
                    background="rgba(255,255,255,0.03)",
                    border="1px solid rgba(255,255,255,0.07)",
                    border_radius="12px",
                    padding="8px 14px",
                    width="100%",
                    max_width="340px",
                    align_items="center",
                    gap="8px",
                    transition="all 0.2s ease",
                    _focus_within={
                        "border_color": "rgba(99,102,241,0.45)",
                        "background": "rgba(99,102,241,0.04)",
                        "box_shadow": "0 0 0 3px rgba(99,102,241,0.08)",
                    },
                ),
                # New project button
                rx.button(
                    rx.html("""<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>"""),
                    rx.text("New Project", font_size="0.875rem", font_weight="700"),
                    background="linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)",
                    color="white",
                    border_radius="12px",
                    padding="10px 20px",
                    cursor="pointer",
                    gap="7px",
                    box_shadow="0 4px 20px rgba(99,102,241,0.3), inset 0 1px 0 rgba(255,255,255,0.1)",
                    transition="all 0.25s cubic-bezier(0.16,1,0.3,1)",
                    _hover={
                        "box_shadow": "0 8px 30px rgba(99,102,241,0.45), inset 0 1px 0 rgba(255,255,255,0.15)",
                        "transform": "translateY(-2px)",
                        "background": "linear-gradient(135deg, #818cf8 0%, #6366f1 100%)",
                    },
                    _active={"transform": "translateY(0)", "box_shadow": "0 2px 8px rgba(99,102,241,0.3)"},
                    on_click=cast(Any, DashboardState.open_modal),
                ),
                width="100%",
                justify="between",
                align_items="center",
                style={"animation": "fadeSlideUp 0.5s cubic-bezier(0.16,1,0.3,1) 0.2s both"},
            ),

            # Projects loading skeleton, grid or empty state
            rx.cond(
                DashboardState.is_loading,
                rx.grid(
                    project_skeleton_card(),
                    project_skeleton_card(),
                    project_skeleton_card(),
                    columns=rx.breakpoints(initial="1", sm="2", md="3"),
                    spacing="5",
                    width="100%",
                ),
                rx.cond(
                    cast(Any, DashboardState.filtered_projects).length() > 0,
                    rx.grid(
                        rx.foreach(DashboardState.filtered_projects, render_project_card),
                        columns=rx.breakpoints(initial="1", sm="2", md="3"),
                        spacing="5",
                        width="100%",
                        style={"animation": "fadeIn 0.4s ease 0.3s both"},
                    ),
                    # Empty state
                    rx.vstack(
                        rx.box(
                            rx.html("""<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"/><line x1="7" y1="2" x2="7" y2="22"/><line x1="17" y1="2" x2="17" y2="22"/>
                                <line x1="2" y1="12" x2="22" y2="12"/><line x1="2" y1="7" x2="7" y2="7"/><line x1="2" y1="17" x2="7" y2="17"/>
                                <line x1="17" y1="17" x2="22" y2="17"/><line x1="17" y1="7" x2="22" y2="7"/>
                            </svg>"""),
                            width="72px", height="72px",
                            border_radius="20px",
                            background="rgba(99,102,241,0.08)",
                            border="1px solid rgba(99,102,241,0.15)",
                            color="#818cf8",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                            margin_bottom="24px",
                        ),
                        rx.heading(
                            "No projects yet",
                            size="5",
                            color="#e4e4e7",
                            font_weight="700",
                            letter_spacing="-0.02em",
                        ),
                        rx.text(
                            "Create your first project to start uploading research documents and asking questions.",
                            color="rgba(113,113,122,0.8)",
                            font_size="0.9rem",
                            text_align="center",
                            max_width="340px",
                            line_height="1.6",
                        ),
                        rx.button(
                            rx.html("""<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>"""),
                            rx.text("Create Project", font_size="0.875rem", font_weight="600"),
                            background="rgba(255,255,255,0.04)",
                            border="1px solid rgba(255,255,255,0.1)",
                            color="#e4e4e7",
                            padding="10px 22px",
                            border_radius="12px",
                            cursor="pointer",
                            gap="7px",
                            margin_top="8px",
                            transition="all 0.2s ease",
                            _hover={
                                "background": "rgba(99,102,241,0.08)",
                                "border_color": "rgba(99,102,241,0.4)",
                                "color": "white",
                                "transform": "translateY(-1px)",
                                "box_shadow": "0 4px 16px rgba(99,102,241,0.15)",
                            },
                            on_click=cast(Any, DashboardState.open_modal),
                        ),
                        padding="80px 24px",
                        background="rgba(16,16,24,0.3)",
                        border="1px dashed rgba(255,255,255,0.07)",
                        border_radius="24px",
                        width="100%",
                        align="center",
                        spacing="3",
                        style={"animation": "fadeSlideUp 0.5s cubic-bezier(0.16,1,0.3,1) 0.3s both"},
                    ),
                ),
            ),

            width="100%",
            max_width="1100px",
            margin="0 auto",
            padding="52px 40px",
            z_index="1",
            spacing="8",
            class_name="page-transition",
        ),

        # ── New Project Modal ─────────────────────────────────────────
        rx.dialog.root(
            rx.dialog.content(
                # Header
                rx.hstack(
                    rx.vstack(
                        rx.heading(
                            "New Project",
                            font_size="1.3rem",
                            font_weight="800",
                            color="#f4f4f5",
                            letter_spacing="-0.03em",
                        ),
                        rx.text(
                            "Give your research project a clear, memorable name.",
                            font_size="0.82rem",
                            color="rgba(161,161,170,0.7)",
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.dialog.close(
                        rx.box(
                            rx.html("""<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>"""),
                            width="32px", height="32px",
                            border_radius="8px",
                            background="rgba(255,255,255,0.04)",
                            border="1px solid rgba(255,255,255,0.08)",
                            color="rgba(161,161,170,0.6)",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                            cursor="pointer",
                            transition="all 0.15s ease",
                            _hover={"background": "rgba(255,255,255,0.08)", "color": "#f4f4f5"},
                        ),
                    ),
                    width="100%",
                    justify="between",
                    align_items="start",
                    margin_bottom="24px",
                ),

                # Input
                rx.box(
                    rx.input(
                        placeholder="e.g. MyBombayFilm",
                        max_length=80,
                        value=DashboardState.new_project_name,
                        on_change=cast(Any, DashboardState.set_new_project_name),
                        background="rgba(255,255,255,0.03)",
                        border="1px solid rgba(255,255,255,0.09)",
                        border_radius="12px",
                        padding="14px 18px",
                        color="#f4f4f5",
                        font_size="0.95rem",
                        width="100%",
                        style={"caret-color": "#818cf8"},
                        _placeholder={"color": "rgba(113,113,122,0.6)"},
                        _focus={
                            "border_color": "rgba(99,102,241,0.5)",
                            "background": "rgba(99,102,241,0.04)",
                            "box_shadow": "0 0 0 3px rgba(99,102,241,0.1)",
                            "outline": "none",
                        },
                    ),
                    width="100%",
                ),

                # Buttons
                rx.hstack(
                    rx.dialog.close(
                        rx.button(
                            "Cancel",
                            background="rgba(255,255,255,0.03)",
                            border="1px solid rgba(255,255,255,0.08)",
                            color="rgba(161,161,170,0.8)",
                            border_radius="10px",
                            padding="10px 20px",
                            font_size="0.875rem",
                            cursor="pointer",
                            transition="all 0.2s ease",
                            _hover={"background": "rgba(255,255,255,0.07)", "color": "white"},
                        )
                    ),
                    rx.button(
                        "Create Project",
                        background="linear-gradient(135deg, #6366f1, #4f46e5)",
                        color="white",
                        border_radius="10px",
                        padding="10px 22px",
                        font_size="0.875rem",
                        font_weight="700",
                        cursor="pointer",
                        box_shadow="0 4px 14px rgba(99,102,241,0.25), inset 0 1px 0 rgba(255,255,255,0.1)",
                        transition="all 0.2s cubic-bezier(0.16,1,0.3,1)",
                        _hover={
                            "box_shadow": "0 6px 20px rgba(99,102,241,0.4)",
                            "transform": "translateY(-1px)",
                        },
                        _active={"transform": "translateY(0)"},
                        on_click=cast(Any, DashboardState.create_project),
                    ),
                    spacing="3",
                    margin_top="28px",
                    justify="end",
                ),

                background="rgba(14,14,20,0.95)",
                backdrop_filter="blur(32px)",
                border="1px solid rgba(255,255,255,0.08)",
                border_radius="24px",
                padding="36px",
                max_width="440px",
                box_shadow="0 32px 80px -16px rgba(0,0,0,0.8), 0 0 0 1px rgba(255,255,255,0.04)",
            ),
            open=DashboardState.is_modal_open,
            on_open_change=cast(Any, DashboardState.set_is_modal_open),
        ),

        # ── Delete Confirmation Modal ─────────────────────────────────
        rx.dialog.root(
            rx.dialog.content(
                # Header
                rx.vstack(
                    rx.heading(
                        "Delete Project?",
                        font_size="1.3rem",
                        font_weight="800",
                        color="#fca5a5",
                        letter_spacing="-0.03em",
                    ),
                    rx.text(
                        f"Are you sure you want to permanently delete '{DashboardState.project_to_delete_name}'? This will delete all documents, chunks, and messages, and cannot be undone.",
                        font_size="0.86rem",
                        color="rgba(161,161,170,0.8)",
                        line_height="1.5",
                    ),
                    spacing="2",
                    align_items="start",
                    margin_bottom="24px",
                ),
                # Buttons
                rx.hstack(
                    rx.button(
                        "Cancel",
                        background="rgba(255,255,255,0.03)",
                        border="1px solid rgba(255,255,255,0.08)",
                        color="rgba(161,161,170,0.8)",
                        border_radius="10px",
                        padding="10px 20px",
                        font_size="0.875rem",
                        cursor="pointer",
                        on_click=cast(Any, DashboardState.close_delete_confirm),
                    ),
                    rx.button(
                        "Delete Project",
                        background="linear-gradient(135deg, #ef4444, #dc2626)",
                        color="white",
                        border_radius="10px",
                        padding="10px 22px",
                        font_size="0.875rem",
                        font_weight="700",
                        cursor="pointer",
                        box_shadow="0 4px 14px rgba(239,68,68,0.25)",
                        on_click=cast(Any, DashboardState.execute_delete_project),
                    ),
                    spacing="3",
                    justify="end",
                ),
                background="rgba(14,14,20,0.95)",
                backdrop_filter="blur(32px)",
                border="1px solid rgba(239,68,68,0.2)",
                border_radius="24px",
                padding="36px",
                max_width="440px",
                box_shadow="0 32px 80px -16px rgba(0,0,0,0.8)",
            ),
            open=DashboardState.is_delete_confirm_open,
            on_open_change=cast(Any, DashboardState.set_is_delete_confirm_open),
        ),

        style=body_style,
        on_mount=cast(Any, DashboardState.load_projects),
    )

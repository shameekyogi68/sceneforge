import reflex as rx
from typing import Any, cast
from sceneforge.styles import ACCENT_COLOR, BACKGROUND_COLOR, SURFACE_COLOR, MUTED_COLOR
from sceneforge.state import State


def app_icon(size: str = "42px", icon_size: str = "18px") -> rx.Component:
    is_compact = (size == "42px")
    text_content = "S·IQ" if is_compact else "ScriptIQ"
    font_size = "1.2rem" if is_compact else "2.2rem"
    
    return rx.box(
        rx.text(
            text_content,
            font_family="'Courier Prime', 'Courier New', Courier, monospace",
            font_weight="800",
            font_size=font_size,
            color="#00F0FF",
            letter_spacing="-0.03em" if not is_compact else "0.02em",
            style={
                "text_shadow": "0 0 15px rgba(0, 240, 255, 0.45)",
            }
        ),
        display="flex",
        align_items="center",
        justify_content="center",
        flex_shrink="0",
    )

def sidebar_nav(active_route: str, user_avatar_char: rx.Var[str] | str, user_email: rx.Var[str] | str, questions_today: rx.Var[int] | int, on_logout: Any, is_online: rx.Var[bool] | bool = True) -> rx.Component:
    def sidebar_button(icon_svg: str, route: str, tooltip: str, is_active: bool) -> rx.Component:
        # Hover indicator logic
        border_left = rx.cond(is_active, "3px solid #00F0FF", "3px solid transparent")
        opacity = rx.cond(is_active, "1.0", "0.5")
        color = rx.cond(is_active, "#00F0FF", "#E2E8F0")
        
        if route:
            btn = rx.link(
                rx.box(
                    rx.html(icon_svg),
                    padding="12px",
                    border_left=border_left,
                    color=color,
                    style={
                        "opacity": opacity,
                        "cursor": "pointer",
                        "transition": "all 0.25s cubic-bezier(0.16,1,0.3,1)",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                        "width": "100%",
                    },
                    _hover={
                        "opacity": "1.0",
                        "color": "#00F0FF",
                        "background": "rgba(0, 240, 255, 0.05)",
                    },
                ),
                href=route,
                width="100%",
                text_decoration="none",
            )
        else:
            btn = rx.box(
                rx.html(icon_svg),
                padding="12px",
                border_left=border_left,
                color=color,
                style={
                    "opacity": opacity,
                    "cursor": "default",
                    "transition": "all 0.25s cubic-bezier(0.16,1,0.3,1)",
                    "display": "flex",
                    "align_items": "center",
                    "justify_content": "center",
                    "width": "100%",
                },
            )
        return rx.tooltip(
            btn,
            content=tooltip,
            side="right",
        )

    # Icons SVGs
    dashboard_svg = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>"""
    chat_svg = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>"""
    library_svg = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/></svg>"""
    settings_svg = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="6" y1="3" x2="6" y2="15"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/></svg>"""
    logout_svg = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>"""

    return rx.vstack(
        # Top Logo Icon
        rx.center(
            app_icon(size="42px", icon_size="18px"),
            padding_y="28px",
            width="100%",
        ),
        
        # Navigation items
        rx.vstack(
            sidebar_button(dashboard_svg, "/dashboard", "Dashboard", active_route == "dashboard"),
            # Chat is context-sensitive (only meaningful inside a project); keep it as a
            # non-interactive indicator so users don't click a dead link.
            sidebar_button(chat_svg, "", "Workspace Chat (Active in Projects)", False),
            spacing="4",
            width="100%",
            align_items="center",
        ),
        
        rx.spacer(),
        
        # Bottom controls
        rx.vstack(
            # Logout
            rx.tooltip(
                rx.box(
                    rx.html(logout_svg),
                    padding="12px",
                    color=MUTED_COLOR,
                    style={
                        "opacity": "0.65",
                        "cursor": "pointer",
                        "transition": "all 0.2s ease",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                        "width": "100%",
                    },
                    _hover={
                        "opacity": "1.0",
                        "color": "#ef4444",
                        "background": "rgba(239, 68, 68, 0.08)",
                    },
                    _active={"transform": "scale(0.95)"},
                    on_click=on_logout,
                ),
                content="Log Out",
                side="right",
            ),
            # User Avatar initials wrapped in Popover Menu
            rx.popover.root(
                rx.popover.trigger(
                    rx.box(
                        rx.center(
                            rx.text(
                                user_avatar_char,
                                font_weight="800",
                                font_size="0.85rem",
                                color="#05080F",
                                text_transform="uppercase",
                            ),
                            width="34px",
                            height="34px",
                            border_radius="50%",
                            background="linear-gradient(135deg, #00F0FF 0%, #0072FF 100%)",
                            box_shadow="0 0 10px rgba(0,240,255,0.4)",
                            cursor="pointer",
                        ),
                        padding_y="16px",
                        width="100%",
                        display="flex",
                        justify_content="center",
                        _active={"transform": "scale(0.95)"},
                    )
                ),
                rx.popover.content(
                    rx.vstack(
                        rx.text("USER PROFILE", class_name="hud-text", font_size="0.6rem", color="#00F0FF", font_weight="700"),
                        rx.text(user_email, font_size="0.8rem", color="#fff", font_weight="600", font_family="JetBrains Mono, monospace", word_break="break-all"),
                        rx.box(width="100%", height="1px", background="rgba(255,255,255,0.06)", margin_y="8px"),
                        
                        rx.hstack(
                            rx.text("DAILY QUERIES", class_name="hud-text", font_size="0.6rem", color="rgba(255,255,255,0.4)"),
                            rx.spacer(),
                            rx.text(questions_today.to(str) + "/100 used", font_size="0.65rem", color="#00F0FF", font_weight="700", font_family="JetBrains Mono, monospace"),
                            width="100%",
                        ),
                        # Quota progress bar
                        rx.box(
                            rx.box(
                                width=rx.cond(questions_today > 100, "100%", questions_today.to(str) + "%"),
                                height="100%",
                                background="linear-gradient(90deg, #00F0FF, #0072FF)",
                                border_radius="2px",
                            ),
                            width="100%",
                            height="4px",
                            background="rgba(255, 255, 255, 0.05)",
                            border_radius="2px",
                            margin_top="4px",
                        ),
                        
                        rx.box(width="100%", height="1px", background="rgba(255,255,255,0.06)", margin_y="8px"),
                        rx.hstack(
                            rx.text("THEME MODE", class_name="hud-text", font_size="0.6rem", color="rgba(255,255,255,0.4)"),
                            rx.spacer(),
                            rx.badge("DARK_ONLY", color_scheme="cyan", variant="solid", font_size="0.55rem"),
                            width="100%",
                            align_items="center",
                        ),
                        align_items="start",
                        spacing="1",
                    ),
                    background="rgba(8, 12, 22, 0.96) !important",
                    backdrop_filter="blur(12px) saturate(140%) !important",
                    border="1px solid rgba(0, 240, 255, 0.25) !important",
                    box_shadow="0 10px 40px rgba(0,0,0,0.8), 0 0 20px rgba(0,240,255,0.08) !important",
                    border_radius="10px !important",
                    padding="16px",
                    width="220px",
                ),
            ),
            spacing="1",
            width="100%",
            align_items="center",
        ),
        
        width="68px",
        height="100vh",
        background="rgba(4, 6, 12, 0.95)",
        border_right="1px solid rgba(255, 255, 255, 0.05)",
        align_items="center",
        flex_shrink="0",
        z_index="40",
    )

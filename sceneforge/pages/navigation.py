import reflex as rx
from typing import Any, cast
from sceneforge.styles import ACCENT_COLOR, BACKGROUND_COLOR, SURFACE_COLOR, MUTED_COLOR

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

def sidebar_nav(active_route: str, user_avatar_char: rx.Var[str] | str, user_email: rx.Var[str] | str, on_logout: Any) -> rx.Component:
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
            sidebar_button(chat_svg, "", "Workspace Chat (Active in Projects)", active_route == "project"),
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
                    color="#ef4444",
                    style={
                        "opacity": "0.6",
                        "cursor": "pointer",
                        "transition": "all 0.2s ease",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                        "width": "100%",
                    },
                    _hover={
                        "opacity": "1.0",
                        "background": "rgba(239, 68, 68, 0.08)",
                    },
                    on_click=on_logout,
                ),
                content="Log Out",
                side="right",
            ),
            # User Avatar initials
            rx.tooltip(
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
                    ),
                    padding_y="16px",
                    width="100%",
                    display="flex",
                    justify_content="center",
                ),
                content=user_email,
                side="right",
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

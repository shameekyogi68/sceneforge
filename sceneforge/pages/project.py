import reflex as rx
from typing import Any, cast
from sceneforge.state import ProjectState
from sceneforge.styles import GLOBAL_CSS, BACKGROUND_COLOR, SURFACE_COLOR, ACCENT_COLOR, TEXT_COLOR, MUTED_COLOR, ERROR_COLOR, SUCCESS_COLOR, FONT_FAMILY

PROJECT_KEYFRAMES = """
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
@keyframes messageIn {
  from { opacity: 0; transform: translateY(12px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes shimmerText {
  0%   { text-shadow: 0 0 5px #00F0FF, 0 0 10px #00F0FF; }
  50%  { text-shadow: 0 0 20px #00F0FF, 0 0 30px #00F0FF; }
  100% { text-shadow: 0 0 5px #00F0FF, 0 0 10px #00F0FF; }
}
@keyframes typingDot {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; box-shadow: none; }
  30%            { transform: translateY(-5px); opacity: 1; box-shadow: 0 0 8px #00F0FF; }
}
@keyframes scanline {
  0%   { background-position: 0 -100vh; }
  100% { background-position: 0 100vh; }
}
@keyframes uploadPulse {
  0%,100% { border-color: rgba(0,240,255,0.2); background: rgba(0,240,255,0.01); }
  50%      { border-color: rgba(0,240,255,0.6); background: rgba(0,240,255,0.08); }
}
@keyframes statusPulse {
  0%,100% { opacity: 1; }
  50%      { opacity: 0.5; }
}
@keyframes glowPulse {
  0%,100% { box-shadow: 0 0 20px rgba(0,240,255,0.1); }
  50%      { box-shadow: 0 0 40px rgba(0,240,255,0.4); }
}
"""

body_style = {
    "font_family": FONT_FAMILY,
    "background_color": BACKGROUND_COLOR,
    "height": "100vh",
    "color": TEXT_COLOR,
    "display": "flex",
    "flex_direction": "column",
    "position": "relative",
    "overflow": "hidden",
}


def project_header() -> rx.Component:
    return rx.hstack(
        # Left: back + breadcrumb
        rx.hstack(
            rx.link(
                rx.hstack(
                    rx.html("""<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="15 18 9 12 15 6"/></svg>"""),
                    rx.text("SYS.DIR", font_size="0.82rem", font_weight="600"),
                    align="center",
                    spacing="1",
                ),
                href="/dashboard",
                color=ACCENT_COLOR,
                text_decoration="none",
                background="rgba(0,240,255,0.05)",
                border=f"1px solid rgba(0,240,255,0.3)",
                border_radius="4px",
                padding="7px 13px",
                transition="all 0.2s cubic-bezier(0.16,1,0.3,1)",
                _hover={
                    "background": "rgba(0,240,255,0.15)",
                    "border_color": ACCENT_COLOR,
                    "box_shadow": f"0 0 10px rgba(0,240,255,0.3)",
                    "transform": "translateX(-2px)",
                },
            ),
            rx.hstack(
                rx.text(
                    "tselaf",
                    font_size="1.1rem",
                    font_weight="800",
                    letter_spacing="0.1em",
                    text_transform="uppercase",
                    style={
                        "color": "#fff",
                        "animation": "shimmerText 3s linear infinite",
                    },
                ),
                rx.text("/", color=MUTED_COLOR, font_size="0.9rem", user_select="none"),
                rx.text(
                    ProjectState.project_name,
                    font_size="0.9rem",
                    color=TEXT_COLOR,
                    font_weight="600",
                    max_width="200px",
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                    text_transform="uppercase",
                    letter_spacing="0.05em",
                ),
                align="center",
                spacing="2",
                margin_left="12px",
            ),
            align="center",
        ),

        # Right: quota pill + sign out
        rx.hstack(
            rx.box(
                rx.text(
                    rx.text("QUOTA: ", color=MUTED_COLOR, as_="span"),
                    ProjectState.remaining_questions,
                    font_size="0.75rem",
                    color=ACCENT_COLOR,
                    font_weight="700",
                    letter_spacing="0.1em",
                ),
                background="rgba(0,240,255,0.05)",
                border=f"1px solid rgba(0,240,255,0.2)",
                border_radius="4px",
                padding="5px 14px",
            ),
            # Clear Chat History Button
            rx.button(
                rx.html("""<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>"""),
                rx.text("PURGE", font_size="0.8rem", font_weight="600", letter_spacing="0.1em",
                        display=rx.breakpoints(initial="none", sm="block")),
                background=SURFACE_COLOR,
                border=f"1px solid {MUTED_COLOR}",
                color=TEXT_COLOR,
                border_radius="4px",
                padding="7px 13px",
                cursor="pointer",
                gap="6px",
                transition="all 0.2s ease",
                _hover={
                    "background": "rgba(255,0,85,0.1)",
                    "border_color": ERROR_COLOR,
                    "color": ERROR_COLOR,
                    "box_shadow": f"0 0 10px rgba(255,0,85,0.3)",
                },
                on_click=cast(Any, lambda: cast(Any, ProjectState).clear_chat),
            ),
            # Sign Out Button
            rx.button(
                rx.html("""<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>"""),
                rx.text("DISCONNECT", font_size="0.8rem", font_weight="600", letter_spacing="0.1em",
                        display=rx.breakpoints(initial="none", sm="block")),
                background=SURFACE_COLOR,
                border=f"1px solid {MUTED_COLOR}",
                color=TEXT_COLOR,
                border_radius="4px",
                padding="7px 13px",
                cursor="pointer",
                gap="6px",
                transition="all 0.2s ease",
                _hover={
                    "background": "rgba(255,0,85,0.1)",
                    "border_color": ERROR_COLOR,
                    "color": ERROR_COLOR,
                    "box_shadow": f"0 0 10px rgba(255,0,85,0.3)",
                },
                on_click=cast(Any, ProjectState.logout),
            ),
            align="center",
            spacing="3",
            margin_left="auto",
        ),

        width="100%",
        padding="12px 28px",
        background="rgba(5,8,15,0.85)",
        backdrop_filter="blur(10px)",
        border_bottom=f"1px solid rgba(0,240,255,0.2)",
        align_items="center",
        flex_shrink="0",
        z_index="10",
    )


def render_doc_item(doc: Any) -> rx.Component:
    status_color = rx.cond(
        doc["status"] == "ready",
        SUCCESS_COLOR,
        rx.cond(doc["status"] == "processing", "#fbbf24", ERROR_COLOR),
    )

    status_icon = rx.cond(
        doc["status"] == "ready",
        rx.html(f"""<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="{SUCCESS_COLOR}" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>"""),
        rx.cond(
            doc["status"] == "processing",
            rx.spinner(size="1", color="amber"),
            rx.html(f"""<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="{ERROR_COLOR}" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>"""),
        ),
    )

    # Simulated pipeline tracker step
    step_val = ProjectState.doc_steps[doc["id"].to(str)]

    stepper_view = rx.cond(
        doc["status"] == "processing",
        rx.vstack(
            rx.hstack(
                rx.cond(
                    step_val > 1,
                    rx.text("✓", color=SUCCESS_COLOR, font_size="0.68rem", font_weight="700"),
                    rx.box(width="6px", height="6px", border_radius="0", background_color="#fbbf24", style={"animation": "statusPulse 1.2s infinite"}),
                ),
                rx.text("EXTRACTING_TEXT", font_size="0.68rem", color=rx.cond(step_val >= 1, TEXT_COLOR, MUTED_COLOR), font_family=FONT_FAMILY, letter_spacing="0.05em"),
                align="center",
                spacing="2",
            ),
            rx.hstack(
                rx.cond(
                    step_val > 2,
                    rx.text("✓", color=SUCCESS_COLOR, font_size="0.68rem", font_weight="700"),
                    rx.cond(
                        step_val == 2,
                        rx.box(width="6px", height="6px", border_radius="0", background_color="#fbbf24", style={"animation": "statusPulse 1.2s infinite"}),
                        rx.box(width="6px", height="6px", border_radius="0", background_color=MUTED_COLOR),
                    ),
                ),
                rx.text("GEN_EMBEDDINGS", font_size="0.68rem", color=rx.cond(step_val >= 2, TEXT_COLOR, MUTED_COLOR), font_family=FONT_FAMILY, letter_spacing="0.05em"),
                align="center",
                spacing="2",
            ),
            rx.hstack(
                rx.cond(
                    step_val > 3,
                    rx.text("✓", color=SUCCESS_COLOR, font_size="0.68rem", font_weight="700"),
                    rx.cond(
                        step_val == 3,
                        rx.box(width="6px", height="6px", border_radius="0", background_color="#fbbf24", style={"animation": "statusPulse 1.2s infinite"}),
                        rx.box(width="6px", height="6px", border_radius="0", background_color=MUTED_COLOR),
                    ),
                ),
                rx.text("INDEXING_VECTORS", font_size="0.68rem", color=rx.cond(step_val >= 3, TEXT_COLOR, MUTED_COLOR), font_family=FONT_FAMILY, letter_spacing="0.05em"),
                align="center",
                spacing="2",
            ),
            spacing="1",
            align_items="start",
            padding_left="24px",
            margin_top="6px",
            width="100%",
        ),
    )

    return rx.vstack(
        rx.hstack(
            # File icon
            rx.box(
                rx.html(f"""<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="{MUTED_COLOR}" stroke-width="1.75"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>"""),
                flex_shrink="0",
            ),
            # Filename + status
            rx.vstack(
                rx.text(
                    doc["filename"],
                    font_size="0.8rem",
                    font_weight="600",
                    color=rx.cond(doc["status"] == "ready", ACCENT_COLOR, TEXT_COLOR),
                    max_width="155px",
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                    cursor=rx.cond(doc["status"] == "ready", "pointer", "default"),
                    _hover=rx.cond(
                        doc["status"] == "ready",
                        {"text_shadow": f"0 0 8px {ACCENT_COLOR}"},
                        {},
                    ),
                    on_click=cast(Any, cast(Any, ProjectState).open_document_preview(doc["filename"].to(str), 1, "")),
                ),
                rx.hstack(
                    status_icon,
                    rx.text(
                        doc["status"],
                        font_size="0.68rem",
                        color=status_color,
                        font_weight="500",
                        text_transform="uppercase",
                        letter_spacing="0.1em",
                        style=rx.cond(
                            doc["status"] == "processing",
                            {"animation": "statusPulse 1.5s ease infinite"},
                            {},
                        ),
                    ),
                    spacing="1",
                    align="center",
                ),
                spacing="0",
                align_items="start",
                flex="1",
                min_width="0",
            ),
            # Delete btn
            rx.button(
                rx.html("""<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>"""),
                background="rgba(255,0,85,0.05)",
                border=f"1px solid rgba(255,0,85,0.2)",
                color=ERROR_COLOR,
                cursor="pointer",
                padding="6px",
                border_radius="4px",
                flex_shrink="0",
                transition="all 0.2s ease",
                _hover={
                    "background": "rgba(255,0,85,0.2)",
                    "border_color": ERROR_COLOR,
                    "box_shadow": f"0 0 10px rgba(255,0,85,0.4)",
                    "transform": "scale(1.1)",
                },
                _active={"transform": "scale(0.95)"},
                on_click=cast(Any, lambda: cast(Any, ProjectState).delete_document(doc["id"], doc["filename"])),
            ),
            width="100%",
            align_items="center",
            gap="10px",
        ),
        stepper_view,
        width="100%",
        padding="10px 12px",
        border_radius="4px",
        background=SURFACE_COLOR,
        border="1px solid rgba(0,240,255,0.1)",
        transition="all 0.15s ease",
        _hover={"background": "rgba(0,240,255,0.05)", "border_color": "rgba(0,240,255,0.3)"},
    )


def sidebar() -> rx.Component:
    return rx.vstack(
        # ── Upload Section ────────────────────────────────────────────
        rx.vstack(
            rx.hstack(
                rx.html(f"""<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="{ACCENT_COLOR}" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 5 5 12"/></svg>"""),
                rx.text(
                    "DATA_INGESTION",
                    font_size="0.68rem",
                    font_weight="700",
                    text_transform="uppercase",
                    letter_spacing="0.1em",
                    color=ACCENT_COLOR,
                ),
                align="center",
                spacing="2",
            ),

            rx.upload(
                rx.vstack(
                    rx.box(
                        rx.html("""<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/></svg>"""),
                        width="40px",
                        height="40px",
                        border_radius="4px",
                        background="rgba(0,240,255,0.1)",
                        border="1px solid rgba(0,240,255,0.4)",
                        color=ACCENT_COLOR,
                        display="flex",
                        align_items="center",
                        justify_content="center",
                    ),
                    rx.text("DRAG PDFs HERE", font_size="0.76rem", font_weight="700", color=TEXT_COLOR, letter_spacing="0.05em"),
                    rx.text("MAX_SIZE: 50MB", font_size="0.68rem", color=MUTED_COLOR, letter_spacing="0.05em"),
                    align="center",
                    spacing="2",
                ),
                id="pdf_upload",
                border=f"1.5px dashed rgba(0,240,255,0.3)",
                background=SURFACE_COLOR,
                border_radius="4px",
                padding="22px 16px",
                width="100%",
                cursor="pointer",
                transition="all 0.25s ease",
                _hover={
                    "border_color": ACCENT_COLOR,
                    "background": "rgba(0,240,255,0.05)",
                    "box_shadow": f"0 0 24px rgba(0,240,255,0.15)",
                },
                style={"animation": "uploadPulse 4s ease-in-out infinite"},
            ),

            rx.cond(
                cast(Any, rx.selected_files("pdf_upload")),
                rx.vstack(
                    rx.text(
                        "TARGET: ", cast(Any, rx.selected_files("pdf_upload")).join(", "),
                        font_size="0.7rem",
                        color=ACCENT_COLOR,
                        line_height="1.5",
                        word_break="break-all",
                    ),
                    rx.button(
                        rx.html("""<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/></svg>"""),
                        rx.text("EXECUTE_UPLOAD", font_size="0.8rem", font_weight="700", letter_spacing="0.05em"),
                        background="rgba(0,240,255,0.15)",
                        border=f"1px solid {ACCENT_COLOR}",
                        color=ACCENT_COLOR,
                        padding="9px 16px",
                        border_radius="4px",
                        cursor="pointer",
                        gap="7px",
                        box_shadow=f"0 0 15px rgba(0,240,255,0.2)",
                        width="100%",
                        transition="all 0.2s ease",
                        _hover={
                            "background": ACCENT_COLOR,
                            "color": BACKGROUND_COLOR,
                            "box_shadow": f"0 0 25px rgba(0,240,255,0.5)",
                            "transform": "translateY(-1px)",
                        },
                        on_click=[cast(Any, ProjectState.handle_upload)(rx.upload_files(upload_id="pdf_upload")), rx.clear_selected_files("pdf_upload")],
                    ),
                    width="100%",
                    spacing="2",
                ),
            ),

            width="100%",
            padding="22px 18px",
            border_bottom="1px solid rgba(0,240,255,0.2)",
            align_items="start",
            spacing="3",
        ),

        # ── Documents Section ─────────────────────────────────────────
        rx.vstack(
            rx.hstack(
                rx.html(f"""<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="{ACCENT_COLOR}" stroke-width="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>"""),
                rx.text(
                    "INDEXED_DATA",
                    font_size="0.68rem",
                    font_weight="700",
                    text_transform="uppercase",
                    letter_spacing="0.1em",
                    color=ACCENT_COLOR,
                ),
                align="center",
                spacing="2",
            ),
            rx.cond(
                cast(Any, ProjectState.documents).length() > 0,
                rx.vstack(
                    rx.foreach(ProjectState.documents, render_doc_item),
                    width="100%",
                    spacing="2",
                ),
                rx.vstack(
                    rx.html(f"""<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{MUTED_COLOR}" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>"""),
                    rx.text(
                        "NO_RECORDS_FOUND",
                        font_size="0.78rem",
                        color=MUTED_COLOR,
                        text_align="center",
                        letter_spacing="0.1em",
                    ),
                    align="center",
                    width="100%",
                    padding="32px 0",
                    spacing="3",
                ),
            ),
            width="100%",
            padding="22px 18px",
            overflow_y="auto",
            align_items="start",
            spacing="3",
            flex="1",
        ),

        background=SURFACE_COLOR,
        border_right="1px solid rgba(0,240,255,0.2)",
        height="100%",
        width="320px",
        flex_shrink="0",
        overflow="hidden",
    )


def render_source_pill(src: Any) -> rx.Component:
    return rx.tooltip(
        rx.box(
            rx.hstack(
                rx.html("""<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>"""),
                rx.text(
                    src.filename, " | p.", src.page,
                    font_size="0.7rem",
                    font_weight="600",
                ),
                align="center",
                spacing="1",
            ),
            background="rgba(0,240,255,0.05)",
            border=f"1px solid rgba(0,240,255,0.4)",
            color=ACCENT_COLOR,
            border_radius="2px",
            padding="4px 11px",
            display="inline-flex",
            align_items="center",
            cursor="pointer",
            transition="all 0.15s ease",
            _hover={
                "background": "rgba(0,240,255,0.2)",
                "border_color": ACCENT_COLOR,
                "color": "#fff",
                "box_shadow": f"0 0 10px rgba(0,240,255,0.4)",
            },
            on_click=cast(Any, lambda: cast(Any, ProjectState).open_document_preview(src.filename, src.page, src.text_preview)),
        ),
        content=src.text_preview,
    )


def render_chat_message(msg: Any) -> rx.Component:
    is_user = msg.role == "user"

    return rx.box(
        rx.vstack(
            rx.box(
                rx.hstack(
                    rx.markdown(
                        msg.content,
                        style={
                            "font_size": "0.91rem",
                            "line_height": "1.65",
                            "color": rx.cond(is_user, "#ffffff", TEXT_COLOR),
                            "font_family": FONT_FAMILY,
                        },
                        flex="1",
                    ),
                    rx.cond(
                        ~is_user,
                        rx.button(
                            rx.html("""<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>"""),
                            background="rgba(255,255,255,0.02)",
                            border="1px solid rgba(255,255,255,0.1)",
                            color=MUTED_COLOR,
                            padding="5px",
                            border_radius="2px",
                            cursor="pointer",
                            transition="all 0.15s ease",
                            _hover={"background": "rgba(0,240,255,0.2)", "border_color": ACCENT_COLOR, "color": ACCENT_COLOR},
                            _active={"transform": "scale(0.95)"},
                            on_click=[rx.set_clipboard(msg.content), rx.toast.success("Copied to clipboard!", style={"background": SURFACE_COLOR, "color": ACCENT_COLOR, "border": f"1px solid {ACCENT_COLOR}"})],
                            margin_left="8px",
                            align_self="start",
                        ),
                        rx.fragment()
                    ),
                    align_items="start",
                    justify_content="between",
                    width="100%",
                ),
                padding="14px 20px",
                border_radius="4px",
                background=rx.cond(
                    is_user,
                    "rgba(0,240,255,0.1)",
                    SURFACE_COLOR,
                ),
                border=rx.cond(
                    is_user,
                    f"1px solid {ACCENT_COLOR}",
                    f"1px solid rgba(0,240,255,0.1)",
                ),
                box_shadow=rx.cond(
                    is_user,
                    f"0 0 15px rgba(0,240,255,0.15)",
                    "none",
                ),
                max_width="85%",
            ),
            # Source pills
            rx.cond(
                cast(Any, msg.sources).length() > 0,
                rx.flex(
                    rx.foreach(msg.sources, render_source_pill),
                    flex_wrap="wrap",
                    gap="6px",
                    margin_top="10px",
                    padding_left="2px",
                ),
            ),
            align_items=rx.cond(is_user, "end", "start"),
            width="100%",
        ),
        width="100%",
        display="flex",
        justify_content=rx.cond(is_user, "end", "start"),
        style={"animation": "messageIn 0.35s cubic-bezier(0.16,1,0.3,1) both"},
    )


def typing_indicator() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.html(f"""
                <div style="display:flex;align-items:center;gap:5px;padding:14px 18px;
                    background:{SURFACE_COLOR};border:1px solid rgba(0,240,255,0.3);
                    border-radius:4px;">
                    <span style="font-size:0.8rem;color:{ACCENT_COLOR};font-weight:700;margin-right:8px;letter-spacing:0.1em;">PROCESSING_QUERY</span>
                    <span style="width:6px;height:6px;background:{ACCENT_COLOR};border-radius:0;animation:typingDot 1.2s ease infinite 0s;display:inline-block;"></span>
                    <span style="width:6px;height:6px;background:{ACCENT_COLOR};border-radius:0;animation:typingDot 1.2s ease infinite 0.2s;display:inline-block;"></span>
                    <span style="width:6px;height:6px;background:{ACCENT_COLOR};border-radius:0;animation:typingDot 1.2s ease infinite 0.4s;display:inline-block;"></span>
                </div>
            """),
            width="100%",
            justify_content="start",
        ),
        width="100%",
        style={"animation": "messageIn 0.3s cubic-bezier(0.16,1,0.3,1) both"},
    )


def welcome_screen() -> rx.Component:
    def example_btn(text: str) -> rx.Component:
        return rx.button(
            rx.text(f"> {text}", font_size="0.8rem", color=ACCENT_COLOR, text_align="left", line_height="1.4", font_family=FONT_FAMILY),
            background="rgba(0,240,255,0.05)",
            border=f"1px solid rgba(0,240,255,0.2)",
            border_radius="4px",
            padding="15px 16px",
            cursor="pointer",
            text_align="left",
            width="100%",
            transition="all 0.2s cubic-bezier(0.16,1,0.3,1)",
            _hover={
                "background": "rgba(0,240,255,0.15)",
                "border_color": ACCENT_COLOR,
                "color": "#fff",
                "box_shadow": f"0 0 15px rgba(0,240,255,0.2)",
            },
            _active={"transform": "scale(0.98)"},
            on_click=cast(Any, lambda: cast(Any, ProjectState).use_example_question(text)),
        )

    return rx.vstack(
        # Warning when no documents uploaded
        rx.cond(
            cast(Any, ProjectState.documents).length() == 0,
            rx.box(
                rx.hstack(
                    rx.html(f"""<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="{ERROR_COLOR}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>"""),
                    rx.text("WARN: SYSTEM LACKS CONTEXT. INGEST DATA TO PROCEED.", font_size="0.8rem", color=ERROR_COLOR, font_weight="700", letter_spacing="0.05em"),
                    align="center",
                    spacing="2",
                ),
                background="rgba(255,0,85,0.1)",
                border=f"1px solid {ERROR_COLOR}",
                border_radius="4px",
                padding="10px 16px",
                margin_bottom="12px",
                width="100%",
                max_width="520px",
                box_shadow=f"0 0 15px rgba(255,0,85,0.2)",
            ),
        ),
        # Cyber icon
        rx.box(
            rx.html(f"""<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <line x1="3" y1="9" x2="21" y2="9"/>
                <line x1="9" y1="21" x2="9" y2="9"/>
            </svg>"""),
            width="80px",
            height="80px",
            border_radius="4px",
            background="rgba(0,240,255,0.1)",
            border=f"1px solid {ACCENT_COLOR}",
            color=ACCENT_COLOR,
            display="flex",
            align_items="center",
            justify_content="center",
            margin_bottom="24px",
            style={"animation": "glowPulse 3s ease-in-out infinite"},
            box_shadow=f"inset 0 0 15px rgba(0,240,255,0.2)",
        ),
        rx.heading(
            "INITIALIZE QUERY_ENGINE",
            size="5",
            color="#fff",
            font_weight="800",
            letter_spacing="0.1em",
            text_align="center",
        ),
        rx.text(
            "SYSTEM AWAITING INPUT PROMPT. SPECIFY PARAMETERS.",
            color=ACCENT_COLOR,
            font_size="0.87rem",
            text_align="center",
            max_width="460px",
            line_height="1.65",
            letter_spacing="0.05em",
        ),
        rx.grid(
            example_btn("Summarize the key plot points"),
            example_btn("What are the main character arcs?"),
            example_btn("List the primary filming locations"),
            example_btn("Explain the themes of the script"),
            columns="2",
            spacing="3",
            width="100%",
            max_width="560px",
            margin_top="16px",
        ),
        width="100%",
        align="center",
        margin="auto",
        padding="40px",
        spacing="4",
        style={"animation": "fadeSlideUp 0.5s cubic-bezier(0.16,1,0.3,1) both"},
    )


def chat_area() -> rx.Component:
    return rx.vstack(
        # ── Message list ──────────────────────────────────────────────
        rx.box(
            rx.cond(
                cast(Any, ProjectState.chat_history).length() > 0,
                rx.vstack(
                    rx.foreach(ProjectState.chat_history, render_chat_message),
                    rx.cond(
                        ProjectState.is_sending,
                        typing_indicator(),
                    ),
                    spacing="5",
                    width="100%",
                    align_items="stretch",
                    padding_bottom="16px",
                ),
                welcome_screen(),
            ),
            id="chat-scroll-container",
            flex="1",
            overflow_y="auto",
            padding="32px 36px 8px",
            width="100%",
            style={
                "scroll-behavior": "smooth",
                "::-webkit-scrollbar": {"width": "6px"},
                "::-webkit-scrollbar-track": {"background": "rgba(0,0,0,0.3)", "border-left": "1px solid rgba(0,240,255,0.1)"},
                "::-webkit-scrollbar-thumb": {"background": ACCENT_COLOR, "border-radius": "0"},
            },
        ),

        # ── Input bar ─────────────────────────────────────────────────
        rx.box(
            rx.hstack(
                rx.text(">", color=ACCENT_COLOR, font_weight="bold", font_size="1.2rem"),
                rx.box(
                    rx.text_area(
                        placeholder="ENTER COMMAND OR QUERY...",
                        value=ProjectState.input_message,
                        on_change=cast(Any, ProjectState.set_input_message),
                        background="transparent",
                        border="none",
                        padding="14px 8px",
                        color="#fff",
                        font_size="0.95rem",
                        font_family=FONT_FAMILY,
                        width="100%",
                        style={"resize": "none", "caret-color": ACCENT_COLOR, "min_height": "52px", "max_height": "120px"},
                        rows="1",
                        _placeholder={"color": MUTED_COLOR, "letter_spacing": "0.05em"},
                        _focus={
                            "outline": "none",
                            "box_shadow": "none",
                        },
                        on_key_down=cast(Any, ProjectState.handle_key_down),
                    ),
                    flex="1",
                    border_bottom=f"2px solid {ACCENT_COLOR}",
                    transition="border-color 0.2s ease",
                    _focus_within={"border_bottom_color": "#fff", "box_shadow": f"0 5px 10px -5px {ACCENT_COLOR}"},
                ),
                # Send button
                rx.button(
                    rx.cond(
                        ProjectState.is_sending,
                        rx.html(f"""<div style="width:16px;height:16px;border:2px solid {ACCENT_COLOR};border-top-color:transparent;border-radius:50%;animation:spin-slow 0.8s linear infinite;"></div>"""),
                        rx.html("""<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>"""),
                    ),
                    background="rgba(0,240,255,0.15)",
                    border=f"1px solid {ACCENT_COLOR}",
                    color=ACCENT_COLOR,
                    border_radius="4px",
                    padding="14px",
                    cursor=rx.cond(ProjectState.is_sending, "not-allowed", "pointer"),
                    height="52px",
                    width="52px",
                    flex_shrink="0",
                    disabled=ProjectState.is_sending,
                    transition="all 0.2s cubic-bezier(0.16,1,0.3,1)",
                    _hover={
                        "background": ACCENT_COLOR,
                        "color": BACKGROUND_COLOR,
                        "box_shadow": f"0 0 20px rgba(0,240,255,0.6)",
                    },
                    _active={"transform": "scale(0.95)"},
                    on_click=cast(Any, ProjectState.send_message),
                ),
                width="100%",
                align_items="end",
                spacing="3",
            ),
            # Hint
            rx.text(
                "SYS.MSG: [ENTER] TO EXEC, [SHIFT+ENTER] FOR NEWLINE",
                font_size="0.65rem",
                color=MUTED_COLOR,
                text_align="left",
                margin_top="12px",
                letter_spacing="0.1em",
            ),
            width="100%",
            padding="24px 36px 32px",
            background=f"linear-gradient(to top, {BACKGROUND_COLOR} 70%, transparent)",
        ),

        height="100%",
        flex="1",
        overflow="hidden",
        justify="between",
        background=f"radial-gradient(circle at center, rgba(0,240,255,0.02) 0%, transparent 70%)",
    )


def preview_inspector_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.box(
                # Modal Header: Document name + page controls + close button
                rx.hstack(
                    rx.vstack(
                        rx.hstack(
                            rx.html(f"""<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{ACCENT_COLOR}" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>"""),
                            rx.heading(
                                ProjectState.selected_preview_filename,
                                font_size="1.2rem",
                                font_weight="800",
                                color="#fff",
                                max_width="320px",
                                overflow="hidden",
                                text_overflow="ellipsis",
                                white_space="nowrap",
                                letter_spacing="0.05em",
                                font_family=FONT_FAMILY,
                            ),
                            align="center",
                            spacing="2",
                        ),
                        rx.text(
                            "DATA_INSPECTOR_MODULE",
                            font_size="0.78rem",
                            color=ACCENT_COLOR,
                            letter_spacing="0.1em",
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    
                    # Page Navigation Controls
                    rx.hstack(
                        rx.button(
                            rx.html("""<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>"""),
                            background="rgba(0,240,255,0.05)",
                            border=f"1px solid rgba(0,240,255,0.3)",
                            color=rx.cond(ProjectState.selected_preview_page > 1, ACCENT_COLOR, MUTED_COLOR),
                            border_radius="4px",
                            padding="6px 10px",
                            cursor=rx.cond(ProjectState.selected_preview_page > 1, "pointer", "default"),
                            disabled=ProjectState.selected_preview_page <= 1,
                            on_click=cast(Any, lambda: cast(Any, ProjectState).open_document_preview(
                                ProjectState.selected_preview_filename, 
                                ProjectState.selected_preview_page - 1
                            )),
                            _hover=rx.cond(
                                ProjectState.selected_preview_page > 1,
                                {"background": "rgba(0,240,255,0.2)", "color": "#fff", "border_color": ACCENT_COLOR},
                                {}
                            ),
                        ),
                        rx.box(
                            rx.text(
                                "PG ", ProjectState.selected_preview_page,
                                font_size="0.82rem",
                                font_weight="700",
                                color=ACCENT_COLOR,
                                letter_spacing="0.1em",
                            ),
                            background="rgba(0,240,255,0.1)",
                            border=f"1px solid {ACCENT_COLOR}",
                            border_radius="4px",
                            padding="5px 12px",
                            display="flex",
                            align_items="center",
                            box_shadow=f"0 0 10px rgba(0,240,255,0.2)",
                        ),
                        rx.button(
                            rx.html("""<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>"""),
                            background="rgba(0,240,255,0.05)",
                            border=f"1px solid rgba(0,240,255,0.3)",
                            color=ACCENT_COLOR,
                            border_radius="4px",
                            padding="6px 10px",
                            cursor="pointer",
                            on_click=cast(Any, lambda: cast(Any, ProjectState).open_document_preview(
                                ProjectState.selected_preview_filename, 
                                ProjectState.selected_preview_page + 1
                            )),
                            _hover={"background": "rgba(0,240,255,0.2)", "color": "#fff", "border_color": ACCENT_COLOR},
                        ),
                        align="center",
                        spacing="2",
                    ),

                    # Close Button
                    rx.button(
                        rx.html("""<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>"""),
                        background="rgba(255,0,85,0.1)",
                        border=f"1px solid {ERROR_COLOR}",
                        color=ERROR_COLOR,
                        border_radius="4px",
                        padding="6px 10px",
                        cursor="pointer",
                        on_click=cast(Any, ProjectState.close_preview_modal),
                        _hover={"background": ERROR_COLOR, "color": "#fff", "box_shadow": f"0 0 15px {ERROR_COLOR}"},
                    ),
                    width="100%",
                    justify="between",
                    align_items="center",
                    margin_bottom="24px",
                    border_bottom=f"1px solid rgba(0,240,255,0.2)",
                    padding_bottom="16px",
                ),

                # Modal Body: Extracted Page Text
                rx.cond(
                    ProjectState.is_preview_loading,
                    # Skeleton loaders during fetch
                    rx.vstack(
                        rx.box(
                            width="100%", height="20px", border_radius="0",
                            background=f"linear-gradient(90deg, rgba(0,240,255,0.05) 25%, rgba(0,240,255,0.15) 50%, rgba(0,240,255,0.05) 75%)",
                            background_size="200% 100%", style={"animation": "skeletonPulse 1.6s infinite linear"},
                        ),
                        rx.box(
                            width="95%", height="20px", border_radius="0",
                            background=f"linear-gradient(90deg, rgba(0,240,255,0.05) 25%, rgba(0,240,255,0.15) 50%, rgba(0,240,255,0.05) 75%)",
                            background_size="200% 100%", style={"animation": "skeletonPulse 1.6s infinite linear 0.2s"},
                        ),
                        rx.box(
                            width="98%", height="20px", border_radius="0",
                            background=f"linear-gradient(90deg, rgba(0,240,255,0.05) 25%, rgba(0,240,255,0.15) 50%, rgba(0,240,255,0.05) 75%)",
                            background_size="200% 100%", style={"animation": "skeletonPulse 1.6s infinite linear 0.4s"},
                        ),
                        rx.box(
                            width="88%", height="20px", border_radius="0",
                            background=f"linear-gradient(90deg, rgba(0,240,255,0.05) 25%, rgba(0,240,255,0.15) 50%, rgba(0,240,255,0.05) 75%)",
                            background_size="200% 100%", style={"animation": "skeletonPulse 1.6s infinite linear 0.6s"},
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    # Extracted text pane
                    rx.box(
                        rx.html(
                            "<div style=\"white-space: pre-wrap; font-family: 'JetBrains Mono', monospace; font-size: 0.92rem; line-height: 1.7; color: #00F0FF; text-shadow: 0 0 2px rgba(0,240,255,0.5);\">"
                            + ProjectState.selected_preview_text +
                            "</div>"
                        ),
                        max_height="480px",
                        overflow_y="auto",
                        padding_right="12px",
                        width="100%",
                        style={
                            "::-webkit-scrollbar": {"width": "6px"},
                            "::-webkit-scrollbar-track": {"background": "rgba(0,0,0,0.3)", "border-left": "1px solid rgba(0,240,255,0.1)"},
                            "::-webkit-scrollbar-thumb": {"background": ACCENT_COLOR, "border-radius": "0"},
                        },
                    ),
                ),

                background=BACKGROUND_COLOR,
                border=f"1px solid {ACCENT_COLOR}",
                border_radius="0",
                padding="32px",
                max_width="720px",
                width="90vw",
                box_shadow=f"0 0 40px rgba(0,240,255,0.15), inset 0 0 20px rgba(0,240,255,0.1)",
                position="relative",
                _before={
                    "content": '""',
                    "position": "absolute",
                    "top": "0", "left": "0", "right": "0", "bottom": "0",
                    "background": "linear-gradient(rgba(0, 240, 255, 0.05) 1px, transparent 1px)",
                    "background_size": "100% 3px",
                    "pointer_events": "none",
                    "z_index": "10",
                    "opacity": "0.3",
                }
            ),
            background="transparent",
            box_shadow="none",
        ),
        open=ProjectState.is_preview_modal_open,
        on_open_change=cast(Any, ProjectState.set_is_preview_modal_open),
    )


def project_page() -> rx.Component:
    from sceneforge.pages.dashboard import loading_bar
    return rx.box(
        rx.html(f"<style>{GLOBAL_CSS}{PROJECT_KEYFRAMES}</style>"),
        loading_bar(cast(Any, ProjectState.is_sending)),

        # CRT Scanline overlay
        rx.box(
            position="absolute",
            top="0", left="0", right="0", bottom="0",
            background="linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px)",
            background_size="100% 4px",
            z_index="100",
            pointer_events="none",
            opacity="0.4",
        ),

        project_header(),

        rx.hstack(
            sidebar(),
            chat_area(),
            height="calc(100vh - 57px)",
            align_items="stretch",
            width="100%",
            class_name="page-transition",
            z_index="1",
            position="relative",
        ),

        preview_inspector_dialog(),

        style=body_style,
        on_mount=cast(Any, ProjectState.on_load_project),
    )


import reflex as rx
from typing import Any, cast
from sceneforge.state import ProjectState
from sceneforge.styles import GLOBAL_CSS

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
  0%   { background-position: -200% center; }
  100% { background-position:  200% center; }
}
@keyframes typingDot {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30%            { transform: translateY(-5px); opacity: 1; }
}
@keyframes orbFloat {
  0%,100% { transform: translate(0,0) scale(1); }
  50%      { transform: translate(15px,-20px) scale(1.04); }
}
@keyframes uploadPulse {
  0%,100% { border-color: rgba(99,102,241,0.2); background: rgba(255,255,255,0.01); }
  50%      { border-color: rgba(99,102,241,0.45); background: rgba(99,102,241,0.04); }
}
@keyframes statusPulse {
  0%,100% { opacity: 1; }
  50%      { opacity: 0.5; }
}
@keyframes glowPulse {
  0%,100% { box-shadow: 0 0 20px rgba(99,102,241,0.1); }
  50%      { box-shadow: 0 0 40px rgba(99,102,241,0.25); }
}
"""

body_style = {
    "font_family": "'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif",
    "background_color": "#080810",
    "height": "100vh",
    "color": "#f4f4f5",
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
                    rx.text("Projects", font_size="0.82rem", font_weight="600"),
                    align="center",
                    spacing="1",
                ),
                href="/dashboard",
                color="#a5b4fc",
                text_decoration="none",
                background="rgba(99,102,241,0.07)",
                border="1px solid rgba(99,102,241,0.18)",
                border_radius="10px",
                padding="7px 13px",
                transition="all 0.2s cubic-bezier(0.16,1,0.3,1)",
                _hover={
                    "background": "rgba(99,102,241,0.14)",
                    "border_color": "rgba(99,102,241,0.4)",
                    "transform": "translateX(-2px)",
                },
            ),
            rx.hstack(
                rx.text(
                    "SceneForge",
                    font_size="1.05rem",
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
                rx.text("/", color="rgba(63,63,70,0.7)", font_size="0.9rem", user_select="none"),
                rx.text(
                    ProjectState.project_name,
                    font_size="0.9rem",
                    color="#e4e4e7",
                    font_weight="600",
                    max_width="200px",
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
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
                    ProjectState.remaining_questions,
                    font_size="0.75rem",
                    color="#818cf8",
                    font_weight="600",
                    letter_spacing="0.01em",
                ),
                background="rgba(99,102,241,0.08)",
                border="1px solid rgba(99,102,241,0.2)",
                border_radius="20px",
                padding="5px 14px",
            ),
            rx.button(
                rx.html("""<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>"""),
                rx.text("Sign Out", font_size="0.8rem", font_weight="600",
                        display=rx.breakpoints(initial="none", sm="block")),
                background="rgba(255,255,255,0.03)",
                border="1px solid rgba(255,255,255,0.07)",
                color="rgba(212,212,216,0.8)",
                border_radius="9px",
                padding="7px 13px",
                cursor="pointer",
                gap="6px",
                transition="all 0.2s ease",
                _hover={
                    "background": "rgba(239,68,68,0.08)",
                    "border_color": "rgba(239,68,68,0.3)",
                    "color": "#fca5a5",
                },
                on_click=cast(Any, ProjectState.logout),
            ),
            align="center",
            spacing="3",
            margin_left="auto",
        ),

        width="100%",
        padding="12px 28px",
        background="rgba(8,8,16,0.75)",
        backdrop_filter="blur(28px) saturate(1.5)",
        border_bottom="1px solid rgba(255,255,255,0.06)",
        align_items="center",
        flex_shrink="0",
        z_index="10",
    )


def render_doc_item(doc: Any) -> rx.Component:
    status_color = rx.cond(
        doc["status"] == "ready",
        "#34d399",
        rx.cond(doc["status"] == "processing", "#fbbf24", "#f87171"),
    )

    status_icon = rx.cond(
        doc["status"] == "ready",
        rx.html("""<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>"""),
        rx.cond(
            doc["status"] == "processing",
            rx.spinner(size="1", color="amber"),
            rx.html("""<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#f87171" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>"""),
        ),
    )

    # Simulated pipeline tracker step
    step_val = ProjectState.doc_steps[doc["id"]]

    stepper_view = rx.cond(
        doc["status"] == "processing",
        rx.vstack(
            rx.hstack(
                rx.cond(
                    step_val > 1,
                    rx.text("✓", color="#34d399", font_size="0.68rem", font_weight="700"),
                    rx.box(width="6px", height="6px", border_radius="50%", background_color="#fbbf24", style={"animation": "statusPulse 1.2s infinite"}),
                ),
                rx.text("Extracting PDF text...", font_size="0.68rem", color=rx.cond(step_val >= 1, "#e4e4e7", "rgba(113,113,122,0.4)")),
                align="center",
                spacing="2",
            ),
            rx.hstack(
                rx.cond(
                    step_val > 2,
                    rx.text("✓", color="#34d399", font_size="0.68rem", font_weight="700"),
                    rx.cond(
                        step_val == 2,
                        rx.box(width="6px", height="6px", border_radius="50%", background_color="#fbbf24", style={"animation": "statusPulse 1.2s infinite"}),
                        rx.box(width="6px", height="6px", border_radius="50%", background_color="rgba(113,113,122,0.4)"),
                    ),
                ),
                rx.text("Generating embeddings...", font_size="0.68rem", color=rx.cond(step_val >= 2, "#e4e4e7", "rgba(113,113,122,0.4)")),
                align="center",
                spacing="2",
            ),
            rx.hstack(
                rx.cond(
                    step_val > 3,
                    rx.text("✓", color="#34d399", font_size="0.68rem", font_weight="700"),
                    rx.cond(
                        step_val == 3,
                        rx.box(width="6px", height="6px", border_radius="50%", background_color="#fbbf24", style={"animation": "statusPulse 1.2s infinite"}),
                        rx.box(width="6px", height="6px", border_radius="50%", background_color="rgba(113,113,122,0.4)"),
                    ),
                ),
                rx.text("Indexing vectors in DB...", font_size="0.68rem", color=rx.cond(step_val >= 3, "#e4e4e7", "rgba(113,113,122,0.4)")),
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
                rx.html("""<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="rgba(161,161,170,0.7)" stroke-width="1.75"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>"""),
                flex_shrink="0",
            ),
            # Filename + status
            rx.vstack(
                rx.text(
                    doc["filename"],
                    font_size="0.8rem",
                    font_weight="600",
                    color="#e4e4e7",
                    max_width="155px",
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                ),
                rx.hstack(
                    status_icon,
                    rx.text(
                        doc["status"],
                        font_size="0.68rem",
                        color=status_color,
                        font_weight="500",
                        text_transform="capitalize",
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
                background="rgba(239,68,68,0.05)",
                border="1px solid rgba(239,68,68,0.12)",
                color="rgba(252,165,165,0.6)",
                cursor="pointer",
                padding="6px",
                border_radius="7px",
                flex_shrink="0",
                transition="all 0.2s ease",
                _hover={
                    "background": "#ef4444",
                    "border_color": "#ef4444",
                    "color": "#fff",
                    "transform": "scale(1.1)",
                },
                _active={"transform": "scale(0.95)"},
                on_click=lambda: cast(Any, ProjectState).delete_document(doc["id"], doc["filename"]),
            ),
            width="100%",
            align_items="center",
            gap="10px",
        ),
        stepper_view,
        width="100%",
        padding="10px 12px",
        border_radius="11px",
        background="rgba(255,255,255,0.02)",
        border="1px solid rgba(255,255,255,0.04)",
        transition="all 0.15s ease",
        _hover={"background": "rgba(255,255,255,0.04)", "border_color": "rgba(255,255,255,0.08)"},
    )


def sidebar() -> rx.Component:
    return rx.vstack(
        # ── Upload Section ────────────────────────────────────────────
        rx.vstack(
            rx.hstack(
                rx.html("""<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="rgba(129,140,248,0.7)" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 5 5 12"/></svg>"""),
                rx.text(
                    "Upload Research",
                    font_size="0.68rem",
                    font_weight="700",
                    text_transform="uppercase",
                    letter_spacing="0.1em",
                    color="rgba(129,140,248,0.7)",
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
                        border_radius="50%",
                        background="rgba(99,102,241,0.1)",
                        border="1px solid rgba(99,102,241,0.2)",
                        color="#818cf8",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                    ),
                    rx.text("Click or drag PDFs here", font_size="0.76rem", font_weight="600", color="#a1a1aa"),
                    rx.text("Max 50 MB per file", font_size="0.68rem", color="rgba(113,113,122,0.6)"),
                    align="center",
                    spacing="2",
                ),
                id="pdf_upload",
                border="1.5px dashed rgba(99,102,241,0.22)",
                background="rgba(255,255,255,0.01)",
                border_radius="14px",
                padding="22px 16px",
                width="100%",
                cursor="pointer",
                transition="all 0.25s ease",
                _hover={
                    "border_color": "#818cf8",
                    "background": "rgba(99,102,241,0.05)",
                    "box_shadow": "0 0 24px rgba(99,102,241,0.08)",
                },
                style={"animation": "uploadPulse 4s ease-in-out infinite"},
            ),

            rx.cond(
                cast(Any, rx.selected_files("pdf_upload")),
                rx.vstack(
                    rx.text(
                        "Selected: ", cast(Any, rx.selected_files("pdf_upload")).join(", "),
                        font_size="0.7rem",
                        color="rgba(165,180,252,0.8)",
                        line_height="1.5",
                    ),
                    rx.button(
                        rx.html("""<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/></svg>"""),
                        rx.text("Upload & Process", font_size="0.8rem", font_weight="700"),
                        background="linear-gradient(135deg, #6366f1, #4f46e5)",
                        color="white",
                        padding="9px 16px",
                        border_radius="10px",
                        cursor="pointer",
                        gap="7px",
                        box_shadow="0 4px 14px rgba(99,102,241,0.25)",
                        width="100%",
                        transition="all 0.2s ease",
                        _hover={
                            "box_shadow": "0 6px 20px rgba(99,102,241,0.4)",
                            "transform": "translateY(-1px)",
                        },
                        on_click=cast(Any, ProjectState.handle_upload)(rx.upload_files(upload_id="pdf_upload")),
                    ),
                    width="100%",
                    spacing="2",
                ),
            ),

            width="100%",
            padding="22px 18px",
            border_bottom="1px solid rgba(255,255,255,0.06)",
            align_items="start",
            spacing="3",
        ),

        # ── Documents Section ─────────────────────────────────────────
        rx.vstack(
            rx.hstack(
                rx.html("""<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="rgba(129,140,248,0.7)" stroke-width="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>"""),
                rx.text(
                    "Documents",
                    font_size="0.68rem",
                    font_weight="700",
                    text_transform="uppercase",
                    letter_spacing="0.1em",
                    color="rgba(129,140,248,0.7)",
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
                    rx.html("""<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="rgba(113,113,122,0.4)" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>"""),
                    rx.text(
                        "No documents yet",
                        font_size="0.78rem",
                        color="rgba(113,113,122,0.5)",
                        text_align="center",
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

        background="rgba(12,12,18,0.5)",
        border_right="1px solid rgba(255,255,255,0.06)",
        backdrop_filter="blur(20px)",
        height="100%",
        width="290px",
        flex_shrink="0",
        overflow="hidden",
    )


def render_source_pill(src: Any) -> rx.Component:
    return rx.tooltip(
        rx.box(
            rx.hstack(
                rx.html("""<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>"""),
                rx.text(
                    src.filename, " p.", src.page,
                    font_size="0.7rem",
                    font_weight="600",
                ),
                align="center",
                spacing="1",
            ),
            background="rgba(99,102,241,0.08)",
            border="1px solid rgba(99,102,241,0.2)",
            color="#a5b4fc",
            border_radius="20px",
            padding="4px 11px",
            display="inline-flex",
            align_items="center",
            cursor="default",
            transition="all 0.15s ease",
            _hover={
                "background": "rgba(99,102,241,0.16)",
                "border_color": "rgba(99,102,241,0.4)",
                "color": "white",
                "transform": "translateY(-1px)",
            },
        ),
        content=src.text_preview,
    )


def render_chat_message(msg: Any) -> rx.Component:
    is_user = msg.role == "user"

    return rx.box(
        rx.vstack(
            # Bubble
            rx.box(
                rx.markdown(
                    msg.content,
                    style={
                        "font_size": "0.91rem",
                        "line_height": "1.65",
                        "color": rx.cond(is_user, "#ffffff", "#e4e4e7"),
                    },
                ),
                padding="14px 20px",
                border_radius="18px",
                background=rx.cond(
                    is_user,
                    "linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)",
                    "rgba(22,22,32,0.6)",
                ),
                border=rx.cond(
                    is_user,
                    "none",
                    "1px solid rgba(255,255,255,0.07)",
                ),
                border_bottom_right_radius=rx.cond(is_user, "4px", "18px"),
                border_bottom_left_radius=rx.cond(is_user, "18px", "4px"),
                box_shadow=rx.cond(
                    is_user,
                    "0 6px 24px rgba(79,70,229,0.3), inset 0 1px 0 rgba(255,255,255,0.1)",
                    "0 4px 16px rgba(0,0,0,0.2)",
                ),
                backdrop_filter=rx.cond(is_user, "none", "blur(16px)"),
                max_width="76%",
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
            rx.html("""
                <div style="display:flex;align-items:center;gap:5px;padding:14px 18px;
                    background:rgba(22,22,32,0.6);border:1px solid rgba(255,255,255,0.07);
                    border-radius:18px;border-bottom-left-radius:4px;
                    backdrop-filter:blur(16px);box-shadow:0 4px 16px rgba(0,0,0,0.2);">
                    <span style="font-size:0.8rem;color:rgba(161,161,170,0.7);font-weight:500;margin-right:8px;">SceneForge is thinking</span>
                    <span style="width:7px;height:7px;background:#818cf8;border-radius:50%;animation:typingDot 1.2s ease infinite 0s;display:inline-block;"></span>
                    <span style="width:7px;height:7px;background:#818cf8;border-radius:50%;animation:typingDot 1.2s ease infinite 0.2s;display:inline-block;"></span>
                    <span style="width:7px;height:7px;background:#818cf8;border-radius:50%;animation:typingDot 1.2s ease infinite 0.4s;display:inline-block;"></span>
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
            rx.text(text, font_size="0.8rem", color="rgba(212,212,216,0.85)", text_align="left", line_height="1.4"),
            background="rgba(255,255,255,0.02)",
            border="1px solid rgba(255,255,255,0.07)",
            border_radius="14px",
            padding="15px 16px",
            cursor="pointer",
            text_align="left",
            width="100%",
            transition="all 0.2s cubic-bezier(0.16,1,0.3,1)",
            _hover={
                "background": "rgba(99,102,241,0.06)",
                "border_color": "rgba(99,102,241,0.3)",
                "color": "white",
                "transform": "translateY(-2px)",
                "box_shadow": "0 6px 20px rgba(99,102,241,0.1)",
            },
            _active={"transform": "translateY(0)"},
            on_click=lambda: cast(Any, ProjectState).use_example_question(text),
        )

    return rx.vstack(
        # Sparkles icon
        rx.box(
            rx.html("""<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
                <path d="M5 3v4"/><path d="M3 5h4"/><path d="M19 17v4"/><path d="M17 19h4"/>
            </svg>"""),
            width="68px",
            height="68px",
            border_radius="20px",
            background="rgba(99,102,241,0.1)",
            border="1px solid rgba(99,102,241,0.2)",
            color="#818cf8",
            display="flex",
            align_items="center",
            justify_content="center",
            margin_bottom="24px",
            style={"animation": "glowPulse 3s ease-in-out infinite"},
        ),
        rx.heading(
            "Ask anything about your research",
            size="5",
            color="#f4f4f5",
            font_weight="800",
            letter_spacing="-0.03em",
            text_align="center",
        ),
        rx.text(
            "Upload PDFs on the left, then ask questions — SceneForge answers only from your files, with exact source citations.",
            color="rgba(161,161,170,0.7)",
            font_size="0.87rem",
            text_align="center",
            max_width="460px",
            line_height="1.65",
        ),
        rx.grid(
            example_btn("Summarize the key plot points"),
            example_btn("What are the main character arcs?"),
            example_btn("List the primary filming locations"),
            example_btn("Explain the themes of the script"),
            columns="2",
            spacing="3",
            width="100%",
            max_width="520px",
            margin_top="8px",
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
            flex="1",
            overflow_y="auto",
            padding="32px 36px 8px",
            width="100%",
            style={
                "scroll-behavior": "smooth",
                "::-webkit-scrollbar": {"width": "4px"},
                "::-webkit-scrollbar-track": {"background": "transparent"},
                "::-webkit-scrollbar-thumb": {"background": "rgba(99,102,241,0.3)", "border-radius": "4px"},
            },
        ),

        # ── Input bar ─────────────────────────────────────────────────
        rx.box(
            rx.hstack(
                rx.box(
                    rx.text_area(
                        placeholder="Ask a question about your documents...",
                        value=ProjectState.input_message,
                        on_change=cast(Any, ProjectState.set_input_message),
                        background="rgba(18,18,26,0.7)",
                        border="1px solid rgba(255,255,255,0.08)",
                        border_radius="16px",
                        padding="14px 18px",
                        color="#f4f4f5",
                        font_size="0.92rem",
                        font_family="'Plus Jakarta Sans', 'Inter', system-ui, sans-serif",
                        width="100%",
                        style={"resize": "none", "caret-color": "#818cf8", "min_height": "52px", "max_height": "120px"},
                        rows="1",
                        _placeholder={"color": "rgba(113,113,122,0.5)"},
                        _focus={
                            "border_color": "rgba(99,102,241,0.4)",
                            "background": "rgba(18,18,26,0.9)",
                            "box_shadow": "0 0 0 3px rgba(99,102,241,0.08)",
                            "outline": "none",
                        },
                        on_key_down=cast(Any, ProjectState.handle_key_down),
                    ),
                    flex="1",
                ),
                # Send button
                rx.button(
                    rx.cond(
                        ProjectState.is_sending,
                        rx.html("""<div style="width:16px;height:16px;border:2px solid rgba(255,255,255,0.3);border-top-color:white;border-radius:50%;animation:spin-slow 0.8s linear infinite;"></div>"""),
                        rx.html("""<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>"""),
                    ),
                    background=rx.cond(
                        ProjectState.is_sending,
                        "rgba(99,102,241,0.4)",
                        "linear-gradient(135deg, #6366f1, #4f46e5)",
                    ),
                    color="white",
                    border_radius="14px",
                    padding="14px 18px",
                    font_size="0.9rem",
                    font_weight="700",
                    cursor=rx.cond(ProjectState.is_sending, "not-allowed", "pointer"),
                    height="52px",
                    width="52px",
                    flex_shrink="0",
                    disabled=ProjectState.is_sending,
                    box_shadow=rx.cond(
                        ProjectState.is_sending,
                        "none",
                        "0 4px 16px rgba(99,102,241,0.3), inset 0 1px 0 rgba(255,255,255,0.1)",
                    ),
                    transition="all 0.2s cubic-bezier(0.16,1,0.3,1)",
                    _hover={
                        "box_shadow": "0 8px 24px rgba(99,102,241,0.45)",
                        "transform": "translateY(-1px) scale(1.02)",
                    },
                    _active={"transform": "translateY(0) scale(0.98)"},
                    on_click=cast(Any, ProjectState.send_message),
                ),
                width="100%",
                align_items="end",
                spacing="3",
            ),
            # Hint
            rx.text(
                "Enter to send  ·  Shift+Enter for new line",
                font_size="0.68rem",
                color="rgba(113,113,122,0.4)",
                text_align="center",
                margin_top="8px",
                letter_spacing="0.02em",
            ),
            width="100%",
            padding="16px 36px 28px",
            background="linear-gradient(to top, rgba(8,8,16,0.95) 70%, transparent)",
        ),

        height="100%",
        flex="1",
        overflow="hidden",
        justify="between",
    )


def project_page() -> rx.Component:
    from sceneforge.pages.dashboard import loading_bar
    return rx.box(
        rx.html(f"<style>{GLOBAL_CSS}{PROJECT_KEYFRAMES}</style>"),
        loading_bar(cast(Any, ProjectState.is_sending)),

        project_header(),

        rx.hstack(
            sidebar(),
            chat_area(),
            height="calc(100vh - 57px)",
            align_items="stretch",
            width="100%",
            class_name="page-transition",
        ),

        style=body_style,
        on_mount=cast(Any, ProjectState.on_load_project),
    )

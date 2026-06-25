import reflex as rx
from typing import Any, cast
from sceneforge.state import ProjectState
from sceneforge.styles import GLOBAL_CSS, BACKGROUND_COLOR, SURFACE_COLOR, ACCENT_COLOR, TEXT_COLOR, MUTED_COLOR, ERROR_COLOR, SUCCESS_COLOR, FONT_FAMILY, SCREENPLAY_FONT_FAMILY
from sceneforge.pages.navigation import sidebar_nav

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
    "width": "100vw",
    "color": TEXT_COLOR,
    "display": "flex",
    "overflow": "hidden",
}

def macos_dots(on_close: Any) -> rx.Component:
    return rx.hstack(
        rx.box(class_name="macos-dot", background_color="#ff5f56", border="1px solid #e0443e", cursor="pointer", on_click=on_close),
        rx.box(class_name="macos-dot", background_color="#ffbd2e", border="1px solid #dfa123"),
        rx.box(class_name="macos-dot", background_color="#27c93f", border="1px solid #1aab29"),
        spacing="2",
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
                rx.text("Extracting Script Pages...", font_size="0.68rem", color=rx.cond(step_val >= 1, TEXT_COLOR, MUTED_COLOR), font_family=FONT_FAMILY, letter_spacing="0.05em"),
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
                rx.text("Analyzing Characters & Plot...", font_size="0.68rem", color=rx.cond(step_val >= 2, TEXT_COLOR, MUTED_COLOR), font_family=FONT_FAMILY, letter_spacing="0.05em"),
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
            # Folder/File icon
            rx.box(
                rx.html(f"""<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="{MUTED_COLOR}" stroke-width="1.75"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>"""),
                flex_shrink="0",
            ),
            # Filename + status
            rx.vstack(
                rx.text(
                    doc["filename"],
                    font_size="0.85rem",
                    font_weight="600",
                    color=rx.cond(doc["status"] == "ready", ACCENT_COLOR, TEXT_COLOR),
                    max_width="190px",
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                    cursor=rx.cond(doc["status"] == "ready", "pointer", "default"),
                    _hover=rx.cond(
                        doc["status"] == "ready",
                        {"text_shadow": f"0 0 8px {ACCENT_COLOR}"},
                        {},
                    ),
                    on_click=cast(Any, lambda: cast(Any, ProjectState).open_document_preview(doc["filename"].to(str), 1, "")),
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
                    align="center",
                    spacing="1",
                ),
                spacing="1",
                align_items="start",
                flex="1",
                min_width="0",
            ),
            rx.spacer(),
            # Delete button
            rx.button(
                rx.html("""<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>"""),
                background="transparent",
                border="none",
                color="rgba(255,255,255,0.4)",
                cursor="pointer",
                padding="6px",
                border_radius="4px",
                flex_shrink="0",
                transition="all 0.2s ease",
                _hover={
                    "color": ERROR_COLOR,
                    "background": "rgba(255,0,85,0.1)",
                },
                on_click=cast(Any, lambda: cast(Any, ProjectState).delete_document(doc["id"], doc["filename"])),
            ),
            width="100%",
            align_items="center",
            gap="10px",
        ),
        stepper_view,
        width="100%",
        padding="12px 14px",
        border_radius="10px",
        background="rgba(255, 255, 255, 0.02)",
        border="1px solid rgba(255, 255, 255, 0.05)",
        transition="all 0.15s ease",
        _hover={"background": "rgba(0,240,255,0.02)", "border_color": "rgba(0,240,255,0.2)"},
    )

def render_source_pill(src: Any) -> rx.Component:
    return rx.tooltip(
        rx.box(
            rx.hstack(
                rx.text(
                    src.filename + " | p." + src.page.to(str),
                    font_size="0.7rem",
                    font_weight="600",
                ),
                align="center",
                spacing="1",
            ),
            background="rgba(0,240,255,0.06)",
            border=f"1px solid rgba(0,240,255,0.25)",
            color=ACCENT_COLOR,
            border_radius="4px",
            padding="4px 10px",
            display="inline-flex",
            align_items="center",
            cursor="pointer",
            transition="all 0.15s ease",
            _hover={
                "background": "rgba(0,240,255,0.15)",
                "border_color": ACCENT_COLOR,
                "color": "#fff",
                "box_shadow": f"0 0 10px rgba(0,240,255,0.3)",
            },
            on_click=cast(Any, lambda: cast(Any, ProjectState).open_document_preview(src.filename, src.page, src.text_preview)),
        ),
        content=src.text_preview,
    )

def render_chat_message(msg: Any) -> rx.Component:
    is_user = msg.role == "user"

    ai_avatar = rx.box(
        rx.html("""<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#00F0FF" stroke-width="2.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>"""),
        width="28px",
        height="28px",
        border_radius="6px",
        background="rgba(0, 240, 255, 0.08)",
        border="1px solid rgba(0, 240, 255, 0.2)",
        display="flex",
        align_items="center",
        justify_content="center",
        flex_shrink="0",
        margin_right="12px",
        margin_top="4px",
    )

    message_content = rx.box(
        rx.vstack(
            rx.cond(
                ~is_user,
                rx.text("STRUCTURAL INTELLIGENCE SYNTHESIS", class_name="hud-text", font_size="0.65rem", color="#00F0FF", font_weight="700", margin_bottom="6px"),
                rx.fragment(),
            ),
            rx.box(
                rx.markdown(
                    msg.content,
                    style={
                        "font_size": "0.91rem",
                        "line_height": "1.65",
                        "color": rx.cond(is_user, "#ffffff", TEXT_COLOR),
                        "font_family": FONT_FAMILY,
                    },
                ),
                border_left=rx.cond(is_user, "none", "2px solid #00F0FF"),
                padding_left=rx.cond(is_user, "0", "16px"),
                margin_left=rx.cond(is_user, "0", "4px"),
                width="100%",
            ),
            # Source pills
            rx.cond(
                cast(Any, msg.sources).length() > 0,
                rx.flex(
                    rx.foreach(msg.sources, render_source_pill),
                    flex_wrap="wrap",
                    gap="6px",
                    margin_top="14px",
                    padding_left=rx.cond(is_user, "0", "20px"),
                ),
                rx.fragment(),
            ),
            align_items="start",
            spacing="1",
            width="100%",
        ),
        padding="16px 20px",
        border_radius="12px",
        background=rx.cond(is_user, "rgba(0, 240, 255, 0.08)", "rgba(8, 12, 22, 0.6)"),
        border=rx.cond(is_user, "1px solid rgba(0, 240, 255, 0.25)", "1px solid rgba(255, 255, 255, 0.04)"),
        box_shadow=rx.cond(is_user, "0 0 15px rgba(0, 240, 255, 0.1)", "none"),
        max_width="85%",
    )

    return rx.box(
        rx.hstack(
            rx.cond(~is_user, ai_avatar, rx.fragment()),
            message_content,
            align_items="start",
            width="100%",
            justify_content=rx.cond(is_user, "end", "start"),
        ),
        width="100%",
        display="flex",
        justify_content=rx.cond(is_user, "end", "start"),
        style={"animation": "messageIn 0.35s cubic-bezier(0.16,1,0.3,1) both"},
    )

def typing_indicator() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(
                rx.html("""<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#00F0FF" stroke-width="2.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>"""),
                width="28px", height="28px", border_radius="6px", background="rgba(0, 240, 255, 0.08)", border="1px solid rgba(0, 240, 255, 0.2)",
                display="flex", align_items="center", justify_content="center", margin_right="12px",
            ),
            rx.box(
                rx.hstack(
                    rx.text("ANALYZING SCREENPLAY...", class_name="hud-text", font_size="0.72rem", color=ACCENT_COLOR, font_weight="700"),
                    rx.box(width="4px", height="4px", background=ACCENT_COLOR, style={"animation": "typingDot 1.2s ease infinite 0s"}),
                    rx.box(width="4px", height="4px", background=ACCENT_COLOR, style={"animation": "typingDot 1.2s ease infinite 0.2s"}),
                    rx.box(width="4px", height="4px", background=ACCENT_COLOR, style={"animation": "typingDot 1.2s ease infinite 0.4s"}),
                    align="center",
                    spacing="1",
                ),
                padding="12px 18px",
                border_radius="10px",
                background="rgba(8, 12, 22, 0.6)",
                border="1px solid rgba(0, 240, 255, 0.2)",
            ),
            align_items="center",
        ),
        width="100%",
        style={"animation": "messageIn 0.3s cubic-bezier(0.16,1,0.3,1) both"},
    )

def welcome_screen() -> rx.Component:
    def example_btn(text: str) -> rx.Component:
        return rx.button(
            rx.text(f"> {text}", font_size="0.8rem", color=ACCENT_COLOR, text_align="left", line_height="1.4", font_family=FONT_FAMILY),
            background="rgba(0, 240, 255, 0.03)",
            border="1px solid rgba(0, 240, 255, 0.15)",
            border_radius="8px",
            padding="14px 18px",
            cursor="pointer",
            text_align="left",
            width="100%",
            transition="all 0.2s cubic-bezier(0.16,1,0.3,1)",
            _hover={
                "background": "rgba(0, 240, 255, 0.08)",
                "border_color": ACCENT_COLOR,
                "box_shadow": "0 0 12px rgba(0, 240, 255, 0.15)",
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
                    rx.text("NO FILES UPLOADED. PLEASE UPLOAD A SCRIPT TO PROCEED.", font_size="0.75rem", color=ERROR_COLOR, font_weight="700", letter_spacing="0.05em"),
                    align="center",
                    spacing="2",
                ),
                background="rgba(255,0,85,0.08)",
                border=f"1px solid {ERROR_COLOR}",
                border_radius="6px",
                padding="10px 16px",
                margin_bottom="12px",
                width="100%",
                box_shadow="0 0 15px rgba(255,0,85,0.15)",
            ),
        ),
        # Creative Pen icon box
        rx.box(
            rx.html("""<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>"""),
            width="72px",
            height="72px",
            border_radius="12px",
            background="rgba(0, 240, 255, 0.06)",
            border="1px solid rgba(0, 240, 255, 0.25)",
            color=ACCENT_COLOR,
            display="flex",
            align_items="center",
            justify_content="center",
            margin_bottom="16px",
            style={"animation": "glowPulse 3s ease-in-out infinite"},
            box_shadow="inset 0 0 12px rgba(0, 240, 255, 0.15)",
        ),
        rx.heading("CREATIVE STUDIO", size="5", color="#fff", font_weight="800", letter_spacing="0.1em", text_align="center"),
        rx.text("ScriptIQ is ready. Select a screenplay from the panel on the right or upload a new one to begin analysis.", color=ACCENT_COLOR, font_size="0.82rem", text_align="center", max_width="430px", line_height="1.6"),
        rx.grid(
            example_btn("Analyze the narrative arc and pacing"),
            example_btn("Extract character relationships & conflicts"),
            example_btn("Break down scenes by location & time"),
            example_btn("Identify core thematic elements & motifs"),
            columns="2",
            spacing="3",
            width="100%",
            max_width="540px",
            margin_top="16px",
        ),
        width="100%",
        align="center",
        margin="auto",
        padding="32px",
        spacing="3",
        style={"animation": "fadeSlideUp 0.5s cubic-bezier(0.16,1,0.3,1) both"},
    )

def chat_area() -> rx.Component:
    return rx.vstack(
        # Header bar of left panel
        rx.box(
            rx.hstack(
                rx.hstack(
                    rx.box(width="5px", height="5px", border_radius="50%", background_color="#00F0FF", style={"animation": "statusPulse 1.2s infinite"}),
                    rx.text("SCREENPLAY_WORKSPACE", class_name="hud-text", font_size="0.65rem", color="rgba(0,240,255,0.7)"),
                    align="center",
                    spacing="2",
                ),
                rx.heading("ScriptIQ / " + ProjectState.project_name, size="5", font_weight="800", color="#fff", letter_spacing="-0.01em", margin_left="8px"),
                rx.spacer(),
                # Queries Quota
                rx.box(
                    rx.hstack(
                        rx.html("""<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#00F0FF" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/></svg>"""),
                        rx.text(
                            rx.text("DAILY LIMIT: ", color="rgba(255,255,255,0.45)", as_="span"),
                            ProjectState.queries_remaining.to(str) + "/100",
                            font_size="0.68rem",
                            color="#00F0FF",
                            font_weight="700",
                        ),
                        align="center",
                        spacing="2",
                    ),
                    background="rgba(0, 240, 255, 0.08)",
                    border="1px solid rgba(0, 240, 255, 0.2)",
                    border_radius="100px",
                    padding="6px 14px",
                ),
                # Share Button
                rx.box(
                    rx.html("""<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>"""),
                    padding="9px",
                    border_radius="6px",
                    border="1px solid rgba(255,255,255,0.1)",
                    color="rgba(255,255,255,0.6)",
                    cursor="pointer",
                    _hover={"color": "#00F0FF", "border_color": "#00F0FF"},
                ),
                # Clear chat (New Chat) Button
                rx.box(
                    rx.html("""<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>"""),
                    padding="9px",
                    border_radius="6px",
                    background="linear-gradient(135deg, #00F0FF 0%, #0072FF 100%)",
                    color="#05080F",
                    cursor="pointer",
                    box_shadow="0 0 10px rgba(0, 240, 255, 0.2)",
                    _hover={"box_shadow": "0 0 16px rgba(0, 240, 255, 0.4)"},
                    on_click=cast(Any, lambda: cast(Any, ProjectState).clear_chat),
                ),
                align="center",
                spacing="3",
            ),
            padding="16px 28px",
            border_bottom="1px solid rgba(255,255,255,0.06)",
            width="100%",
        ),

        # Message List scroll window
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
            padding="24px 28px",
            width="100%",
            style={
                "scroll-behavior": "smooth",
                "::-webkit-scrollbar": {"width": "4px"},
                "::-webkit-scrollbar-track": {"background": "rgba(0,0,0,0.1)"},
                "::-webkit-scrollbar-thumb": {"background": "rgba(0,240,255,0.2)", "border-radius": "2px"},
            },
        ),

        # ── Input bar ─────────────────────────────────────────────────
        rx.box(
            rx.vstack(
                rx.hstack(
                    # Paperclip attach SVG
                    rx.box(
                        rx.html("""<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>"""),
                        color="rgba(255,255,255,0.45)",
                        padding="10px",
                        cursor="pointer",
                        _hover={"color": "#00F0FF"},
                    ),
                    rx.input(
                        placeholder="Analyze specific sequence or character arc...",
                        value=ProjectState.input_message,
                        on_change=cast(Any, ProjectState.set_input_message),
                        background="transparent",
                        border="none",
                        outline="none",
                        color="#fff",
                        font_size="0.9rem",
                        font_family=FONT_FAMILY,
                        width="100%",
                        style={"caret-color": ACCENT_COLOR},
                        _placeholder={"color": MUTED_COLOR},
                        on_key_down=cast(Any, ProjectState.handle_key_down),
                    ),
                    # Send button
                    rx.button(
                        rx.cond(
                            ProjectState.is_sending,
                            rx.spinner(size="1"),
                            rx.html("""<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>"""),
                        ),
                        background="linear-gradient(135deg, #00F0FF 0%, #8B5CF6 100%)",
                        color="#ffffff",
                        border="none",
                        border_radius="6px",
                        padding="10px",
                        cursor=rx.cond(ProjectState.is_sending, "not-allowed", "pointer"),
                        height="36px",
                        width="36px",
                        flex_shrink="0",
                        disabled=ProjectState.is_sending,
                        box_shadow="0 0 10px rgba(0,240,255,0.2)",
                        transition="all 0.2s cubic-bezier(0.16,1,0.3,1)",
                        _hover={
                            "box_shadow": "0 0 18px rgba(0,240,255,0.45)",
                            "transform": "scale(1.05)",
                        },
                        on_click=cast(Any, ProjectState.send_message),
                    ),
                    width="100%",
                    align_items="center",
                    gap="12px",
                    background="rgba(6, 9, 16, 0.75)",
                    border="1px solid rgba(255,255,255,0.06)",
                    border_radius="10px",
                    padding="6px 12px",
                    _focus_within={"border_color": "#00F0FF", "box_shadow": "0 0 16px rgba(0,240,255,0.1)"},
                ),
                # Hints
                rx.hstack(
                    rx.hstack(
                        rx.box(width="5px", height="5px", border_radius="50%", background_color="#00F0FF"),
                        rx.text("MODE: SCRIPT_EXPERT", class_name="hud-text", font_size="0.58rem", color="rgba(0,240,255,0.7)"),
                        align="center",
                        spacing="1",
                    ),
                    rx.spacer(),
                    rx.text("SHIFT + ENTER FOR MULTI-LINE ANALYSIS", class_name="hud-text", font_size="0.58rem", color="rgba(255,255,255,0.3)"),
                    width="100%",
                    padding_x="4px",
                ),
                spacing="2",
                width="100%",
            ),
            width="100%",
            padding="16px 28px 24px",
            border_top="1px solid rgba(255,255,255,0.04)",
        ),

        height="100%",
        width="50%",
        overflow="hidden",
        justify="between",
        border_right="1px solid rgba(255, 255, 255, 0.05)",
    )

def live_inspection_panel() -> rx.Component:
    # ── Upload panel (shown when selected_preview_filename == "") ─────
    upload_panel = rx.vstack(
        rx.vstack(
            rx.text("UPLOAD SCRIPT", class_name="hud-text", font_size="0.65rem", color="#00F0FF", font_weight="700"),
            rx.upload(
                rx.vstack(
                    rx.box(
                        rx.html("""<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/></svg>"""),
                        width="38px",
                        height="38px",
                        border_radius="50%",
                        background="rgba(0, 240, 255, 0.08)",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        color="#00F0FF",
                    ),
                    rx.text("DRAG PDFs HERE", font_size="0.75rem", font_weight="700", color="#fff", letter_spacing="0.05em"),
                    rx.text("MAX_SIZE: 50MB", font_size="0.68rem", color=MUTED_COLOR),
                    align="center",
                    spacing="2",
                ),
                id="workspace_pdf_upload",
                border="1.5px dashed rgba(0, 240, 255, 0.25)",
                background="rgba(8, 12, 22, 0.6)",
                border_radius="12px",
                padding="24px 16px",
                width="100%",
                cursor="pointer",
            ),
            rx.cond(
                cast(Any, rx.selected_files("workspace_pdf_upload")),
                rx.vstack(
                    rx.text(
                        "File: " + cast(Any, rx.selected_files("workspace_pdf_upload")).join(", "),
                        font_size="0.72rem",
                        color="#00F0FF",
                        word_break="break-all",
                    ),
                    rx.button(
                        "UPLOAD PDF",
                        background="linear-gradient(135deg, #00F0FF 0%, #0072FF 100%)",
                        color="#05080F",
                        font_weight="700",
                        font_size="0.75rem",
                        padding="8px",
                        width="100%",
                        border_radius="6px",
                        cursor="pointer",
                        on_click=[
                            cast(Any, ProjectState.handle_upload)(rx.upload_files(upload_id="workspace_pdf_upload")),
                            rx.clear_selected_files("workspace_pdf_upload")
                        ],
                    ),
                    spacing="2",
                    width="100%",
                ),
            ),
            width="100%",
            spacing="3",
        ),

        # Spacer line
        rx.box(width="100%", height="1px", background="rgba(255,255,255,0.06)", margin_y="8px"),

        # Documents list
        rx.vstack(
            rx.text("SCRIPTS & STORY BIBLES", class_name="hud-text", font_size="0.65rem", color="#00F0FF", font_weight="700"),
            rx.cond(
                cast(Any, ProjectState.documents).length() > 0,
                rx.vstack(
                    rx.foreach(ProjectState.documents, render_doc_item),
                    width="100%",
                    spacing="2",
                ),
                rx.vstack(
                    rx.html("""<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>"""),
                    rx.text("NO FILES UPLOADED", font_size="0.75rem", color="rgba(255,255,255,0.3)"),
                    align="center",
                    width="100%",
                    padding="32px 0",
                    spacing="2",
                ),
            ),
            width="100%",
            align_items="start",
            spacing="3",
            flex="1",
            overflow_y="auto",
            style={
                "::-webkit-scrollbar": {"width": "3px"},
                "::-webkit-scrollbar-thumb": {"background": "rgba(255,255,255,0.08)"},
            },
        ),

        width="100%",
        height="100%",
        spacing="5",
        padding="28px 24px",
    )

    # ── Document viewer (shown when selected_preview_filename != "") ─────
    viewer_panel = rx.vstack(
        # Inspector Header details
        rx.hstack(
            rx.vstack(
                rx.heading(ProjectState.selected_preview_filename, size="5", font_weight="800", color="#fff", max_width="220px", overflow="hidden", text_overflow="ellipsis", white_space="nowrap"),
                rx.text(
                    ProjectState.preview_page_label,
                    font_size="0.7rem",
                    color="rgba(255,255,255,0.4)",
                    font_family="'JetBrains Mono', monospace",
                ),
                align_items="start",
                spacing="1",
            ),
            rx.spacer(),
            # Page navigations circles
            rx.hstack(
                rx.box(
                    rx.html("""<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>"""),
                    width="28px", height="28px", border_radius="50%",
                    background="rgba(255,255,255,0.03)", border="1px solid rgba(255,255,255,0.08)",
                    color=rx.cond(ProjectState.selected_preview_page > 1, "#00F0FF", "rgba(255,255,255,0.2)"),
                    cursor=rx.cond(ProjectState.selected_preview_page > 1, "pointer", "default"),
                    display="flex", align_items="center", justify_content="center",
                    on_click=cast(Any, lambda: cast(Any, ProjectState).open_document_preview(ProjectState.selected_preview_filename, ProjectState.selected_preview_page - 1)),
                    _hover=rx.cond(ProjectState.selected_preview_page > 1, {"border_color": "#00F0FF", "background": "rgba(0,240,255,0.06)"}, {}),
                ),
                rx.box(
                    rx.html("""<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>"""),
                    width="28px", height="28px", border_radius="50%",
                    background="rgba(255,255,255,0.03)", border="1px solid rgba(255,255,255,0.08)",
                    color="#00F0FF",
                    cursor="pointer",
                    display="flex", align_items="center", justify_content="center",
                    on_click=cast(Any, lambda: cast(Any, ProjectState).open_document_preview(ProjectState.selected_preview_filename, ProjectState.selected_preview_page + 1)),
                    _hover={"border_color": "#00F0FF", "background": "rgba(0,240,255,0.06)"},
                ),
                spacing="2",
            ),
            width="100%",
            align_items="center",
        ),

        # Document Card matching Cyber Director mock
        rx.box(
            # macOS Window top bar
            rx.hstack(
                macos_dots(cast(Any, ProjectState.close_preview_modal)),
                rx.spacer(),
                rx.text("LIVE INSPECTION V2.0", class_name="hud-text", font_size="0.58rem", color="#00F0FF", font_weight="700"),
                width="100%",
                padding="12px 18px",
                border_bottom="1px solid rgba(255,255,255,0.05)",
                background="rgba(4, 6, 12, 0.4)",
            ),
            
            # Script Content Pane
            rx.cond(
                ProjectState.is_preview_loading,
                # Shimmer skeleton
                rx.vstack(
                    rx.box(width="90%", height="14px", background="rgba(0,240,255,0.05)", style={"animation": "statusPulse 1.2s infinite"}),
                    rx.box(width="95%", height="14px", background="rgba(255,255,255,0.03)", style={"animation": "statusPulse 1.2s infinite 0.2s"}),
                    rx.box(width="80%", height="14px", background="rgba(255,255,255,0.03)", style={"animation": "statusPulse 1.2s infinite 0.4s"}),
                    padding="28px", width="100%", spacing="3",
                ),
                # Actual script pages
                rx.box(
                    # Section Start Mono marker
                    rx.center(
                        rx.text("SECTION_START", class_name="hud-text", font_size="0.6rem", color="rgba(255,255,255,0.25)"),
                        padding_bottom="14px",
                    ),
                    rx.html(f"""
                        <div style="font-family:{SCREENPLAY_FONT_FAMILY}; font-size:0.88rem; line-height:1.75; color:#cbd5e1; white-space:pre-wrap; font-style:italic;">
{ProjectState.selected_preview_text}
                        </div>
                    """),
                    
                    # cited highlight segment if any
                    rx.cond(
                        ProjectState.selected_preview_highlight != "",
                        rx.vstack(
                            rx.text("CITED TEXT SEGMENT", class_name="hud-text", font_size="0.58rem", color="#00F0FF", font_weight="700"),
                            rx.text(ProjectState.selected_preview_highlight, font_family=SCREENPLAY_FONT_FAMILY, font_size="0.88rem", font_style="normal", color="#fff"),
                            border_left="2px solid #00F0FF",
                            padding_left="14px",
                            margin_top="18px",
                            spacing="1",
                            align_items="start",
                        ),
                        rx.fragment(),
                    ),
                    padding="24px 28px",
                    overflow_y="auto",
                    flex="1",
                    style={
                        "::-webkit-scrollbar": {"width": "3px"},
                        "::-webkit-scrollbar-thumb": {"background": "rgba(0,240,255,0.2)"},
                    },
                ),
            ),

            class_name="glass-panel",
            width="100%",
            flex="1",
            overflow="hidden",
            display="flex",
            flex_direction="column",
        ),

        width="100%",
        height="100%",
        spacing="3",
        padding="28px 24px",
    )

    return rx.box(
        rx.cond(
            ProjectState.selected_preview_filename == "",
            upload_panel,
            viewer_panel,
        ),
        width="50%",
        height="100%",
        background="rgba(4, 6, 12, 0.15)",
    )

def project_page() -> rx.Component:
    return rx.box(
        rx.cond(ProjectState.is_sending, rx.box(
            width="100%", height="2px",
            background="linear-gradient(90deg, #00F0FF 0%, #00B8FF 50%, #00F0FF 100%)",
            background_size="200% 100%", position="absolute", top="0", left="0", z_index="1000",
            style={"animation": "pulseNeon 1.5s linear infinite"}
        ), rx.fragment()),
        rx.html(f"<style>{GLOBAL_CSS}{PROJECT_KEYFRAMES}</style>"),

        # Main Layout container
        rx.hstack(
            sidebar_nav("project", ProjectState.user_avatar_char, ProjectState.user_email, ProjectState.logout),
            # Workspace splitscreen
            rx.hstack(
                chat_area(),
                live_inspection_panel(),
                width="calc(100vw - 68px)",
                height="100vh",
                align_items="stretch",
                spacing="0",
            ),
            width="100%",
            height="100vh",
            align_items="start",
            spacing="0",
        ),

        style=body_style,
        on_mount=cast(Any, ProjectState.on_load_project),
    )

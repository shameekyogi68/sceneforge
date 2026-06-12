import reflex as rx
from typing import Any
from sceneforge.state import ProjectState

body_style = {
    "font_family": "'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif",
    "background_color": "#09090b",
    "height": "100vh",
    "color": "#f4f4f5",
    "display": "flex",
    "flex_direction": "column",
    "position": "relative",
    "overflow": "hidden",
}

def project_header() -> rx.Component:
    """Header with breadcrumbs, remaining questions and Sign Out."""
    return rx.hstack(
        # Breadcrumbs
        rx.hstack(
            rx.link(
                rx.hstack(
                    rx.icon("arrow_left", size=14),
                    rx.text("Projects"),
                    align="center",
                    spacing="1",
                ),
                href="/dashboard",
                color="#a5b4fc",
                font_size="0.85rem",
                font_weight="700",
                background_color="rgba(255, 255, 255, 0.03)",
                border="1px solid rgba(255, 255, 255, 0.08)",
                border_radius="10px",
                padding="8px 14px",
                text_decoration="none",
                _hover={"background_color": "rgba(255, 255, 255, 0.08)", "border_color": "rgba(99, 102, 241, 0.4)", "transform": "translateX(-2px)"},
                transition="all 0.25s cubic-bezier(0.16, 1, 0.3, 1)",
            ),
            rx.hstack(
                rx.text("SceneForge", font_size="1.15rem", font_weight="800",
                        background_image="linear-gradient(135deg, #a5b4fc, #c084fc)",
                        background_clip="text", text_fill_color="transparent"),
                rx.text("/", color="#3f3f46", font_size="0.9rem", user_select="none"),
                rx.text(ProjectState.project_name, font_size="0.95rem", color="#e4e4e7", font_weight="600"),
                align="center",
                spacing="2",
                margin_left="12px",
            ),
            align="center",
        ),
        
        # Remaining questions
        rx.text(ProjectState.remaining_questions, margin_left="auto", font_size="0.8rem", color="#818cf8", font_weight="600",
                background_color="rgba(99, 102, 241, 0.08)", padding="6px 14px", border_radius="20px", border="1px solid rgba(99, 102, 241, 0.2)"),
        
        # Sign Out
        rx.button(
            rx.icon("log_out", size=14),
            rx.text("Sign Out"),
            background_color="rgba(255, 255, 255, 0.03)",
            border="1px solid rgba(255, 255, 255, 0.08)",
            color="#d4d4d8",
            border_radius="10px",
            padding="8px 14px",
            font_size="0.82rem",
            font_weight="600",
            cursor="pointer",
            _hover={"background_color": "rgba(239, 68, 68, 0.08)", "border_color": "rgba(239, 68, 68, 0.25)", "color": "#fca5a5"},
            on_click=ProjectState.logout,
        ),
        width="100%",
        padding="14px 32px",
        background_color="rgba(9, 9, 11, 0.65)",
        backdrop_filter="blur(24px)",
        border_bottom="1px solid rgba(255, 255, 255, 0.08)",
        align_items="center",
        z_index="10",
    )

def render_doc_item(doc: Any) -> rx.Component:
    """Sidebar document list item."""
    status_color = rx.cond(
        doc["status"] == "ready",
        "#34d399",
        rx.cond(
            doc["status"] == "processing",
            "#fbbf24",
            "#f87171"
        )
    )
    
    return rx.hstack(
        rx.icon("file_text", size=18, color="#a1a1aa"),
        rx.vstack(
            rx.text(doc["filename"], font_size="0.82rem", font_weight="600", color="#e4e4e7", max_width="160px", overflow="hidden", text_overflow="ellipsis", white_space="nowrap"),
            rx.hstack(
                rx.cond(
                    doc["status"] == "processing",
                    rx.spinner(size="1", color="amber"),
                ),
                rx.text(doc["status"], font_size="0.7rem", color=status_color, font_weight="500", text_transform="capitalize"),
                spacing="1",
                align="center",
            ),
            spacing="1",
            align_items="start",
        ),
        # Delete document button
        rx.button(
            rx.icon("trash_2", size=13),
            background_color="rgba(239, 68, 68, 0.05)",
            border="1px solid rgba(239, 68, 68, 0.15)",
            color="#fca5a5",
            cursor="pointer",
            padding="5px",
            border_radius="6px",
            margin_left="auto",
            _hover={"background_color": "#ef4444", "border_color": "#ef4444", "color": "#ffffff"},
            on_click=lambda: ProjectState.delete_document(doc["id"], doc["filename"]),
        ),
        width="100%",
        padding="12px 14px",
        border_radius="12px",
        background_color="rgba(255, 255, 255, 0.02)",
        border="1px solid rgba(255, 255, 255, 0.04)",
        align_items="center",
    )

def sidebar() -> rx.Component:
    """Workspace left sidebar with file upload and document list."""
    return rx.vstack(
        # Section 1: Upload Research
        rx.vstack(
            rx.heading("Upload Research", size="3", font_weight="700", text_transform="uppercase", letter_spacing="0.08em", color="#818cf8"),
            rx.upload(
                rx.vstack(
                    rx.box(
                        rx.icon("cloud_upload", size=22),
                        width="44px",
                        height="44px",
                        border_radius="50%",
                        background_color="rgba(99, 102, 241, 0.08)",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        color="#818cf8",
                        margin_bottom="6px",
                    ),
                    rx.text("Click or drag PDFs here", font_size="0.78rem", font_weight="600"),
                    rx.text("Max 50 MB per file", font_size="0.7rem", color="#a1a1aa"),
                    align="center",
                    spacing="1",
                ),
                id="pdf_upload",
                border="2px dashed rgba(99, 102, 241, 0.25)",
                background_color="rgba(255, 255, 255, 0.01)",
                border_radius="16px",
                padding="20px 16px",
                width="100%",
                cursor="pointer",
                _hover={"border_color": "#818cf8", "background_color": "rgba(99, 102, 241, 0.05)"},
            ),
            # Upload start button if files selected
            rx.cond(
                rx.selected_files("pdf_upload"),
                rx.vstack(
                    rx.text("Selected: ", rx.selected_files("pdf_upload").join(", "), font_size="0.72rem", color="#cbd5e1"),
                    rx.button(
                        "Upload and Process",
                        background="linear-gradient(135deg, #6366f1, #4f46e5)",
                        color="white",
                        font_size="0.8rem",
                        padding="8px 16px",
                        border_radius="8px",
                        cursor="pointer",
                        on_click=ProjectState.handle_upload(rx.upload_files(upload_id="pdf_upload")),
                        width="100%",
                    ),
                    width="100%",
                    spacing="2",
                ),
            ),
            width="100%",
            padding="24px 20px",
            border_bottom="1px solid rgba(255, 255, 255, 0.08)",
            align_items="start",
        ),
        
        # Section 2: Documents list
        rx.vstack(
            rx.heading("Documents", size="3", font_weight="700", text_transform="uppercase", letter_spacing="0.08em", color="#818cf8"),
            rx.cond(
                ProjectState.documents.length() > 0,
                rx.vstack(
                    rx.foreach(ProjectState.documents, render_doc_item),
                    width="100%",
                    spacing="2",
                ),
                rx.text("No documents yet.", id="no-docs", font_size="0.82rem", color="#71717a", width="100%", text_align="center", padding="32px 0"),
            ),
            width="100%",
            padding="24px 20px",
            overflow_y="auto",
        ),
        
        background_color="rgba(18, 18, 22, 0.45)",
        border_right="1px solid rgba(255, 255, 255, 0.08)",
        backdrop_filter="blur(16px)",
        height="100%",
        width="320px",
    )

def render_source_pill(src: Any) -> rx.Component:
    """Renders a hoverable tooltip source citation pill."""
    return rx.tooltip(
        rx.box(
            rx.icon("link", size=12, style={"opacity": 0.7, "display": "inline-block", "margin-right": "6px"}),
            rx.text(src.filename, " (p.", src.page, ")", font_size="0.72rem", font_weight="600", display="inline-block"),
            background_color="rgba(99, 102, 241, 0.08)",
            border="1px solid rgba(99, 102, 241, 0.2)",
            color="#a5b4fc",
            border_radius="20px",
            padding="4px 12px",
            cursor="default",
            _hover={"background_color": "rgba(99, 102, 241, 0.16)", "border_color": "rgba(99, 102, 241, 0.4)", "color": "white"},
            display="inline-flex",
            align_items="center",
        ),
        content=src.text_preview,
    )

def render_chat_message(msg: Any) -> rx.Component:
    """Renders a single chat bubble."""
    is_user = msg.role == "user"
    
    # Custom markdown-like rendering of chat bubbles in Reflex
    bubble_content = rx.markdown(
        msg.content,
        style={
            "font_size": "0.94rem",
            "line_height": "1.6",
            "color": rx.cond(is_user, "#ffffff", "#e4e4e7"),
        }
    )
    
    return rx.box(
        rx.vstack(
            rx.box(
                bubble_content,
                padding="16px 22px",
                border_radius="20px",
                background=rx.cond(is_user, "linear-gradient(135deg, #4f46e5, #6366f1)", "rgba(24, 24, 27, 0.5)"),
                border=rx.cond(is_user, "none", "1px solid rgba(255, 255, 255, 0.06)"),
                border_bottom_right_radius=rx.cond(is_user, "4px", "20px"),
                border_bottom_left_radius=rx.cond(is_user, "20px", "4px"),
                box_shadow=rx.cond(is_user, "0 6px 20px rgba(79, 70, 229, 0.25)", "0 4px 16px rgba(0,0,0,0.15)"),
                backdrop_filter=rx.cond(is_user, "none", "blur(12px)"),
                max_width="78%",
            ),
            # Render sources if assistant response
            rx.cond(
                msg.sources.length() > 0,
                rx.flex(
                    rx.foreach(msg.sources, render_source_pill),
                    flex_wrap="wrap",
                    gap="8px",
                    margin_top="12px",
                    padding_left="2px",
                ),
            ),
            align_items=rx.cond(is_user, "end", "start"),
            width="100%",
        ),
        width="100%",
        display="flex",
        justify_content=rx.cond(is_user, "end", "start"),
    )

def chat_area() -> rx.Component:
    """Right-side chat pane."""
    return rx.vstack(
        # Message History
        rx.box(
            rx.cond(
                ProjectState.chat_history.length() > 0,
                rx.vstack(
                    rx.foreach(ProjectState.chat_history, render_chat_message),
                    # Show typing indicator
                    rx.cond(
                        ProjectState.is_sending,
                        rx.hstack(
                            rx.box(
                                rx.hstack(
                                    rx.spinner(size="1", color="indigo"),
                                    rx.text("SceneForge is thinking...", font_size="0.88rem", color="#a1a1aa"),
                                    align="center",
                                    spacing="2",
                                ),
                                padding="14px 20px",
                                border_radius="20px",
                                background="rgba(24, 24, 27, 0.5)",
                                border="1px solid rgba(255, 255, 255, 0.06)",
                                border_bottom_left_radius="4px",
                            ),
                            width="100%",
                            justify_content="start",
                        ),
                    ),
                    spacing="5",
                    width="100%",
                    align_items="stretch",
                ),
                # Welcome panel if chat history empty
                rx.vstack(
                    rx.box(
                        rx.icon("sparkles", size=36),
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
                    rx.heading("Ask anything about your research", size="5", color="#f4f4f5", font_weight="800", margin_bottom="14px"),
                    rx.text("Upload PDFs on the left, then ask questions — SceneForge answers only from your files, with exact source citations.",
                            color="#a1a1aa", font_size="0.9rem", text_align="center", max_width="480px", margin_bottom="32px"),
                    # Example questions grid
                    rx.grid(
                        rx.button("Summarize the key plot points", on_click=lambda: ProjectState.use_example_question("Summarize the key plot points"),
                                  background_color="rgba(255, 255, 255, 0.02)", border="1px solid rgba(255, 255, 255, 0.06)", color="#d4d4d8", padding="14px", border_radius="12px", font_size="0.8rem", cursor="pointer", _hover={"background_color": "rgba(99, 102, 241, 0.05)", "border_color": "rgba(99, 102, 241, 0.35)", "color": "white"}),
                        rx.button("What are the main character arcs?", on_click=lambda: ProjectState.use_example_question("What are the main character arcs?"),
                                  background_color="rgba(255, 255, 255, 0.02)", border="1px solid rgba(255, 255, 255, 0.06)", color="#d4d4d8", padding="14px", border_radius="12px", font_size="0.8rem", cursor="pointer", _hover={"background_color": "rgba(99, 102, 241, 0.05)", "border_color": "rgba(99, 102, 241, 0.35)", "color": "white"}),
                        rx.button("List the primary filming locations", on_click=lambda: ProjectState.use_example_question("List the primary filming locations"),
                                  background_color="rgba(255, 255, 255, 0.02)", border="1px solid rgba(255, 255, 255, 0.06)", color="#d4d4d8", padding="14px", border_radius="12px", font_size="0.8rem", cursor="pointer", _hover={"background_color": "rgba(99, 102, 241, 0.05)", "border_color": "rgba(99, 102, 241, 0.35)", "color": "white"}),
                        rx.button("Explain the themes of the script", on_click=lambda: ProjectState.use_example_question("Explain the themes of the script"),
                                  background_color="rgba(255, 255, 255, 0.02)", border="1px solid rgba(255, 255, 255, 0.06)", color="#d4d4d8", padding="14px", border_radius="12px", font_size="0.8rem", cursor="pointer", _hover={"background_color": "rgba(99, 102, 241, 0.05)", "border_color": "rgba(99, 102, 241, 0.35)", "color": "white"}),
                        columns="2",
                        spacing="3",
                        width="100%",
                        max_width="540px",
                    ),
                    width="100%",
                    align="center",
                    margin="auto",
                )
            ),
            flex="1",
            overflow_y="auto",
            padding="32px 40px",
            width="100%",
        ),
        
        # Input Bar
        rx.hstack(
            rx.text_area(
                placeholder="Ask a question...",
                value=ProjectState.input_message,
                on_change=ProjectState.set_input_message,
                background="rgba(24, 24, 27, 0.7)",
                border="1px solid rgba(255, 255, 255, 0.08)",
                border_radius="16px",
                padding="16px 20px",
                color="#f4f4f5",
                font_size="0.95rem",
                width="100%",
                style={"resize": "none"},
                rows="1",
                _focus={"border_color": "rgba(99, 102, 241, 0.45)", "background": "rgba(24, 24, 27, 0.85)"},
                # Enter to submit, Shift+Enter for newline
                on_key_down=ProjectState.handle_key_down,
            ),
            rx.button(
                rx.text("Send"),
                rx.icon("send", size=16),
                background="linear-gradient(135deg, #6366f1, #4f46e5)",
                color="white",
                border_radius="16px",
                padding="16px 24px",
                font_size="0.95rem",
                font_weight="700",
                cursor="pointer",
                height="100%",
                disabled=ProjectState.is_sending,
                on_click=ProjectState.send_message,
            ),
            width="100%",
            padding="24px 40px 32px",
            align_items="stretch",
            spacing="3",
        ),
        height="100%",
        flex="1",
    )

def project_page() -> rx.Component:
    """The complete visual Project workspace page."""
    return rx.box(
        project_header(),
        rx.hstack(
            sidebar(),
            chat_area(),
            height="calc(100vh - 61px)",
            align_items="stretch",
            width="100%",
        ),
        style=body_style,
        on_mount=ProjectState.on_load_project,
    )

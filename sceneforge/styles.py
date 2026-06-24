"""
styles.py — Shared global CSS injected into every page via rx.html.
"""

# Cyber Tech-Noir Theme Constants
BACKGROUND_COLOR = "#05080F"
SURFACE_COLOR = "rgba(10, 15, 25, 0.8)"
ACCENT_COLOR = "#00F0FF"
TEXT_COLOR = "#E2E8F0"
MUTED_COLOR = "rgba(161, 161, 170, 0.7)"
ERROR_COLOR = "#FF0055"
SUCCESS_COLOR = "#00FF88"
FONT_FAMILY = "'JetBrains Mono', monospace"

GLOBAL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html {
    scroll-behavior: smooth;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
}

body {
    margin: 0; padding: 0;
    background-color: #05080F;
    background-image: 
        linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
    background-size: 40px 40px;
    background-position: center top;
    color: #E2E8F0;
    font-family: 'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif;
    overflow-x: hidden;
}

/* Thin premium scrollbars */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: rgba(5, 8, 15, 0.8); }
::-webkit-scrollbar-thumb { background: rgba(0, 240, 255, 0.3); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0, 240, 255, 0.6); }

/* Text selection */
::selection { background: rgba(0, 240, 255, 0.3); color: #ffffff; }

/* Radix dialog overlay */
.rt-BaseDialogOverlay {
    backdrop-filter: blur(8px) saturate(1.2) !important;
    background: rgba(5, 8, 15, 0.8) !important;
}

/* Global transitions and keyframes */
@keyframes pageFadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes pulseNeon {
    0% { box-shadow: 0 0 5px rgba(0, 240, 255, 0.2); }
    50% { box-shadow: 0 0 15px rgba(0, 240, 255, 0.6); }
    100% { box-shadow: 0 0 5px rgba(0, 240, 255, 0.2); }
}

/* Apply fade-in to every main page content wrapper */
.page-transition {
    animation: pageFadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
}

/* Tech-Noir Glass Panel */
.glass-panel {
    background: rgba(13, 20, 36, 0.7) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.04) !important;
    border-radius: 12px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
}

/* Cyber Input styling */
.premium-input {
    background: rgba(10, 15, 25, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    color: #E2E8F0 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.95rem !important;
    transition: all 0.2s ease-in-out !important;
}
.premium-input:focus-within {
    border-color: #00F0FF !important;
    background: rgba(10, 15, 25, 0.95) !important;
    box-shadow: 0 0 12px rgba(0, 240, 255, 0.15) !important;
    outline: none !important;
}

/* Cyber Button Hover Glow */
.cyber-button-hover:hover {
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.4);
    border-color: rgba(0, 240, 255, 0.8) !important;
}

.cyber-button-purple:hover {
    box-shadow: 0 0 15px rgba(139, 92, 246, 0.4);
    border-color: rgba(139, 92, 246, 0.8) !important;
}

/* HUD Text Class */
.hud-text {
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Document preview highlights */
.search-highlight {
    background-color: rgba(0, 240, 255, 0.2) !important;
    color: #00F0FF !important;
    border-radius: 2px;
    padding: 0 2px;
    font-family: 'JetBrains Mono', monospace;
    border-bottom: 1px solid #00F0FF;
}
"""



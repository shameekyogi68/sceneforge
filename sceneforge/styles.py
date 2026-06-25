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
FONT_FAMILY = "'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif"
SCREENPLAY_FONT_FAMILY = "'Courier Prime', 'Courier New', Courier, monospace"

GLOBAL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Courier+Prime:ital,wght@0,400;0,700;1,400;1,700&display=swap');


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
    color: #E2E8F0;
    font-family: 'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif;
    overflow-x: hidden;
}

/* Thin premium scrollbars */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: rgba(5, 8, 15, 0.85); }
::-webkit-scrollbar-thumb { background: rgba(0, 240, 255, 0.25); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0, 240, 255, 0.55); }

/* Text selection */
::selection { background: rgba(0, 240, 255, 0.25); color: #ffffff; }

/* Radix dialog overlay */
.rt-BaseDialogOverlay {
    backdrop-filter: blur(10px) saturate(1.3) !important;
    background: rgba(4, 6, 12, 0.85) !important;
}

/* Global transitions and keyframes */
@keyframes pageFadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes pulseNeon {
    0% { box-shadow: 0 0 5px rgba(0, 240, 255, 0.2); }
    50% { box-shadow: 0 0 18px rgba(0, 240, 255, 0.55); }
    100% { box-shadow: 0 0 5px rgba(0, 240, 255, 0.2); }
}

@keyframes progressGlow {
    0% { background-position: 0% 0; }
    100% { background-position: -200% 0; }
}

@keyframes scanBar {
    0% { transform: translateX(-50px); }
    100% { transform: translateX(140px); }
}


/* Apply fade-in to every main page content wrapper */
.page-transition {
    animation: pageFadeIn 0.45s cubic-bezier(0.16, 1, 0.3, 1) both;
}

/* Tech-Noir Glass Panel */
.glass-panel {
    background: rgba(8, 12, 22, 0.85) !important;
    backdrop-filter: blur(6px) saturate(1.2) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 16px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5) !important;
    transition: border-color 0.2s cubic-bezier(0.16, 1, 0.3, 1), transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.glass-panel-glow {
    background: rgba(8, 12, 22, 0.85) !important;
    backdrop-filter: blur(6px) saturate(1.2) !important;
    border: 1px solid rgba(0, 240, 255, 0.15) !important;
    border-radius: 16px;
    box-shadow: 0 8px 32px 0 rgba(0, 240, 255, 0.05), inset 0 0 12px rgba(0, 240, 255, 0.05) !important;
    transition: border-color 0.2s cubic-bezier(0.16, 1, 0.3, 1), transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

/* Cyber Input styling */
.premium-input {
    background: rgba(6, 9, 16, 0.85) !important;
    border: 1px solid rgba(255, 255, 255, 0.07) !important;
    color: #E2E8F0 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.9rem !important;
    transition: border-color 0.15s ease, background-color 0.15s ease, box-shadow 0.15s ease !important;
}
.premium-input:focus-within {
    border-color: #00F0FF !important;
    background: rgba(6, 9, 16, 0.98) !important;
    box-shadow: 0 0 16px rgba(0, 240, 255, 0.18) !important;
    outline: none !important;
}

/* Cyber Button Hover Glow */
.cyber-button-hover:hover {
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.45);
    border-color: rgba(0, 240, 255, 0.8) !important;
}

/* HUD Text Class */
.hud-text {
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* Sidebar Styling */
.sidebar-tab {
    position: relative;
    opacity: 0.55;
    transition: all 0.2s ease;
}
.sidebar-tab:hover {
    opacity: 0.95;
    color: #00F0FF;
}
.sidebar-tab-active {
    position: relative;
    opacity: 1;
    color: #00F0FF;
}

/* macOS colored dots style */
.macos-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
}

/* Document preview highlights */
.search-highlight {
    background-color: rgba(0, 240, 255, 0.18) !important;
    color: #00F0FF !important;
    border-radius: 2px;
    padding: 0 2px;
    font-family: 'JetBrains Mono', monospace;
    border-bottom: 1px solid #00F0FF;
}
"""

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
APP_VERSION = "4.0"

GLOBAL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&display=swap');
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

/* Hide Reflex watermark badge — multiple selectors for resilience */
a[href="https://reflex.dev"],
a[href*="reflex.dev"],
[href="https://reflex.dev"] {
    display: none !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

/* Connection status indicator */
.connection-indicator {
    position: fixed;
    bottom: 1rem;
    left: 1rem;
    z-index: 9999;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
    border-radius: 9999px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    backdrop-filter: blur(8px) saturate(1.2);
    background: rgba(8, 12, 22, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: rgba(255, 255, 255, 0.7);
    transition: opacity 0.3s ease, transform 0.3s ease;
}
.connection-indicator.online {
    border-color: rgba(0, 255, 136, 0.3);
    color: rgba(0, 255, 136, 0.9);
}
.connection-indicator.offline {
    border-color: rgba(255, 0, 85, 0.4);
    color: rgba(255, 0, 85, 0.9);
}
.connection-indicator.hidden {
    opacity: 0;
    transform: translateY(10px);
    pointer-events: none;
}
.connection-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
    box-shadow: 0 0 6px currentColor;
}

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

@keyframes borderPulse {
  0%, 100% { border-color: rgba(0, 240, 255, 0.25); box-shadow: 0 0 10px rgba(0, 240, 255, 0.05); }
  50%      { border-color: rgba(0, 240, 255, 0.7); box-shadow: 0 0 20px rgba(0, 240, 255, 0.2); }
}

@keyframes slideLeft {
  from { transform: translateX(100%); opacity: 0; }
  to   { transform: translateX(0); opacity: 1; }
}

@keyframes statusPulse {
  0%, 100% { opacity: 1; }
  50%      { opacity: 0.5; }
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

/* Premium Input — ensure typed text clears the icon */
.premium-input input {
    padding-left: 8px !important;
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

/* Muted dashed card that glows on hover */
.dashed-new-project-card {
    border: 1px dashed rgba(255, 255, 255, 0.1) !important;
    color: rgba(255, 255, 255, 0.4) !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
.dashed-new-project-card:hover {
    border-color: #00F0FF !important;
    background: rgba(0, 240, 255, 0.03) !important;
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.15) !important;
    color: #00F0FF !important;
}
.dashed-new-project-card:hover svg {
    stroke: #00F0FF !important;
}
.dashed-new-project-card:hover .dashed-icon-holder {
    border-color: #00F0FF !important;
    background: rgba(0, 240, 255, 0.08) !important;
}

/* Quota progress bar fill */
.quota-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #00F0FF, #0072FF);
    border-radius: 2px;
    transition: width 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    min-width: 2px;
}

/* Radix Dialog content dark theme override */
.rt-DialogContent {
    background: rgba(8, 12, 22, 0.96) !important;
    border: 1px solid rgba(0, 240, 255, 0.15) !important;
    backdrop-filter: blur(12px) saturate(1.4) !important;
}

/* Markdown content in chat messages */
.rx-Markdown p { margin: 0 0 0.5em 0; }
.rx-Markdown p:last-child { margin-bottom: 0; }
.rx-Markdown code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82em;
    background: rgba(0, 240, 255, 0.08);
    color: #00F0FF;
    padding: 1px 5px;
    border-radius: 3px;
}
.rx-Markdown pre {
    background: rgba(4, 6, 12, 0.8);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    padding: 12px 16px;
    overflow-x: auto;
    margin: 8px 0;
}
.rx-Markdown pre code {
    background: transparent;
    padding: 0;
    color: #E2E8F0;
}
.rx-Markdown ul, .rx-Markdown ol {
    padding-left: 1.4em;
    margin: 4px 0;
}
.rx-Markdown li { margin: 2px 0; }
.rx-Markdown strong { color: #ffffff; font-weight: 700; }
.rx-Markdown em { color: rgba(226,232,240,0.8); }
.rx-Markdown h1,.rx-Markdown h2,.rx-Markdown h3 {
    color: #ffffff;
    font-weight: 700;
    margin: 10px 0 4px;
    letter-spacing: -0.01em;
}
"""

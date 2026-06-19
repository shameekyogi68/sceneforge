"""
styles.py — Shared global CSS injected into every page via rx.html.
"""

GLOBAL_CSS = """
*, *::before, *::after { box-sizing: border-box; }

html {
    scroll-behavior: smooth;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
}

body {
    margin: 0; padding: 0;
    background: #06060c;
    color: #f4f4f5;
    font-family: 'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif;
    overflow-x: hidden;
}

/* Thin premium scrollbars */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(8, 8, 16, 0.3); }
::-webkit-scrollbar-thumb { background: rgba(99, 102, 241, 0.2); border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.03); }
::-webkit-scrollbar-thumb:hover { background: rgba(99, 102, 241, 0.45); }

/* Text selection */
::selection { background: rgba(99, 102, 241, 0.35); color: #ffffff; }

/* Radix dialog overlay */
.rt-BaseDialogOverlay {
    backdrop-filter: blur(16px) saturate(1.3) !important;
    background: rgba(4, 4, 8, 0.6) !important;
}

/* Global transitions and keyframes */
@keyframes spin-slow {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}

@keyframes progressGlow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes pageFadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes gradientBg {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Shimmer skeleton loader */
@keyframes skeletonPulse {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* Pulse glow for buttons and cards */
@keyframes pulseGlowRing {
    0% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(99, 102, 241, 0); }
    100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); }
}

/* Apply fade-in to every main page content wrapper */
.page-transition {
    animation: pageFadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
}

/* High-fidelity glassmorphic panel styling */
.glass-panel {
    background: rgba(14, 14, 24, 0.65) !important;
    backdrop-filter: blur(24px) saturate(1.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.07) !important;
    box-shadow: 
        0 24px 64px -16px rgba(0, 0, 0, 0.65), 
        0 1px 0 0 rgba(255, 255, 255, 0.08) inset,
        0 0 0 1px rgba(255, 255, 255, 0.03) inset !important;
}

/* Modern input styling */
.premium-input {
    background: rgba(8, 8, 14, 0.7) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
.premium-input:focus-within {
    border-color: rgba(99, 102, 241, 0.5) !important;
    background: rgba(8, 8, 14, 0.95) !important;
    box-shadow: 
        0 0 0 3px rgba(99, 102, 241, 0.12),
        0 4px 16px -4px rgba(99, 102, 241, 0.15) !important;
}

/* Premium Highlight style for document preview citations */
.search-highlight {
    background-color: rgba(234, 179, 8, 0.3) !important;
    color: #ffffff !important;
    border-radius: 4px;
    padding: 1px 4px;
    font-weight: 600;
    box-shadow: 0 0 8px rgba(234, 179, 8, 0.4);
    border: 1px solid rgba(234, 179, 8, 0.5);
}
"""



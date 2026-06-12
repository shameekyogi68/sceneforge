"""
styles.py — Shared global CSS injected into every page via rx.html.
"""

GLOBAL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400;1,600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html {
    scroll-behavior: smooth;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
}

body {
    margin: 0; padding: 0;
    background: #080810;
    font-family: 'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif;
}

/* Thin indigo scrollbars */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.28); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.5); }

/* Text selection */
::selection { background: rgba(99,102,241,0.28); color: #f4f4f5; }

/* Radix dialog overlay */
.rt-BaseDialogOverlay {
    backdrop-filter: blur(10px) !important;
    background: rgba(0,0,0,0.65) !important;
}

/* Shared animation used on loading screens */
@keyframes spin-slow {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
"""

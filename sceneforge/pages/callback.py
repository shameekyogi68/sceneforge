import reflex as rx
from sceneforge.state import AuthState
from sceneforge.styles import GLOBAL_CSS

CALLBACK_KEYFRAMES = """
@keyframes spin-slow {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.95); }
  to   { opacity: 1; transform: scale(1); }
}
"""


def callback_page() -> rx.Component:
    """Minimal loading screen shown briefly during OAuth token extraction."""
    return rx.center(
        rx.html(f"<style>{GLOBAL_CSS}{CALLBACK_KEYFRAMES}</style>"),
        # Client-side hash extraction, cookie injection, and redirect
        rx.html("""
            <script>
            (function() {
                function parseJwt(token) {
                    try {
                        const base64Url = token.split('.')[1];
                        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
                        const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
                            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
                        }).join(''));
                        return JSON.parse(jsonPayload);
                    } catch (e) {
                        return null;
                    }
                }

                const hash = window.location.hash;
                if (!hash) {
                    window.location.href = "/login";
                    return;
                }

                const cleanHash = hash.startsWith('#') ? hash.substring(1) : hash;
                const params = new URLSearchParams(cleanHash);
                const accessToken = params.get("access_token");
                const refreshToken = params.get("refresh_token");

                if (!accessToken) {
                    window.location.href = "/login";
                    return;
                }

                const payload = parseJwt(accessToken);
                if (!payload || !payload.sub) {
                    window.location.href = "/login";
                    return;
                }

                const userId = payload.sub;

                // Set cookies exactly as expected by Reflex rx.Cookie
                const maxAge = 31536000; // 1 year
                document.cookie = "token=" + encodeURIComponent(accessToken) + "; path=/; secure; SameSite=Strict; max-age=" + maxAge;
                document.cookie = "user_id=" + encodeURIComponent(userId) + "; path=/; secure; SameSite=Strict; max-age=" + maxAge;
                if (refreshToken) {
                    document.cookie = "refresh_token=" + encodeURIComponent(refreshToken) + "; path=/; secure; SameSite=Strict; max-age=" + maxAge;
                }

                // Redirect to dashboard
                window.location.href = "/dashboard";
            })();
            </script>
        """),
        rx.vstack(
            rx.heading(
                "ScriptIQ",
                size="8",
                font_weight="800",
                letter_spacing="-0.04em",
                style={
                    "background": "linear-gradient(135deg, #c7d2fe 0%, #a5b4fc 40%, #c084fc 100%)",
                    "-webkit-background-clip": "text",
                    "-webkit-text-fill-color": "transparent",
                    "background-clip": "text",
                },
            ),
            # Spinner
            rx.html("""
                <div style="
                    width: 24px; height: 24px;
                    border: 2px solid rgba(99,102,241,0.2);
                    border-top-color: #818cf8;
                    border-radius: 50%;
                    animation: spin-slow 0.8s linear infinite;
                "></div>
            """),
            rx.text(
                "Completing sign-in...",
                color="rgba(161,161,170,0.7)",
                font_size="0.88rem",
                font_weight="500",
                letter_spacing="0.01em",
            ),
            align="center",
            spacing="4",
            style={"animation": "fadeIn 0.4s ease both"},
        ),
        height="100vh",
        background_color="#080810",
        width="100%",
        font_family="'Plus Jakarta Sans', 'Inter', system-ui, sans-serif",
    )

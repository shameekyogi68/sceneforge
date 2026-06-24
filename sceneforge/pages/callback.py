import reflex as rx
from sceneforge.state import AuthState
from sceneforge.styles import GLOBAL_CSS, BACKGROUND_COLOR, ACCENT_COLOR, TEXT_COLOR, MUTED_COLOR, FONT_FAMILY

CALLBACK_KEYFRAMES = """
@keyframes spin-slow {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.95); }
  to   { opacity: 1; transform: scale(1); }
}
@keyframes shimmerText {
  0%   { text-shadow: 0 0 5px #00F0FF, 0 0 10px #00F0FF; }
  50%  { text-shadow: 0 0 20px #00F0FF, 0 0 30px #00F0FF; }
  100% { text-shadow: 0 0 5px #00F0FF, 0 0 10px #00F0FF; }
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
        rx.box(
            position="absolute",
            top="0", left="0", right="0", bottom="0",
            background="linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px)",
            background_size="100% 4px",
            z_index="0",
            pointer_events="none",
            opacity="0.4",
        ),
        rx.vstack(
            rx.heading(
                "tselaf",
                size="8",
                font_weight="800",
                letter_spacing="0.1em",
                text_transform="uppercase",
                style={
                    "color": "#fff",
                    "animation": "shimmerText 3s linear infinite",
                },
            ),
            # Spinner
            rx.html(f"""
                <div style="
                    width: 24px; height: 24px;
                    border: 2px solid rgba(0,240,255,0.2);
                    border-top-color: {ACCENT_COLOR};
                    border-radius: 0;
                    animation: spin-slow 0.8s linear infinite;
                "></div>
            """),
            rx.text(
                "SYS.AUTH_HANDSHAKE_IN_PROGRESS",
                color=MUTED_COLOR,
                font_size="0.88rem",
                font_weight="700",
                letter_spacing="0.05em",
            ),
            align="center",
            spacing="4",
            style={"animation": "fadeIn 0.4s ease both"},
            z_index="1",
            position="relative",
        ),
        height="100vh",
        background_color=BACKGROUND_COLOR,
        width="100%",
        font_family=FONT_FAMILY,
    )

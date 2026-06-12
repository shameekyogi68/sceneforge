import reflex as rx
from sceneforge.pages.login import login_page
from sceneforge.pages.dashboard import dashboard_page
from sceneforge.pages.project import project_page
from sceneforge.state import State

app = rx.App()

# Register pages
app.add_page(login_page, route="/login")
app.add_page(dashboard_page, route="/dashboard", on_load=State.check_auth)
app.add_page(project_page, route="/project")

# Index page redirects dynamically based on session status
@rx.page(route="/", on_load=State.check_auth)
def index():
    return rx.center(
        rx.spinner(size="3", color="indigo"),
        height="100vh",
        background_color="#09090b",
        width="100%",
    )

import reflex as rx
from sceneforge.sceneforge import app

print("Reflex config:")
print("  api_url:", rx.config.get_config().api_url)
print("  cors_allowed_origins:", rx.config.get_config().cors_allowed_origins)

print("Socket.io instance:")
print("  sio:", app.sio)
if app.sio:
    # Print allowed origins evaluated by socketio
    print("  sio cors_allowed_origins:", getattr(app.sio, "_cors_allowed_origins", None))
    print("  sio cors:", getattr(app.sio, "cors", None))

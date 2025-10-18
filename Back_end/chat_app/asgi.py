# ...existing code...
import os
# set DJANGO_SETTINGS_MODULE before importing anything that imports Django models/apps
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat_app.settings")

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import ChatApp.routing
# ...existing code...

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(ChatApp.routing.websocket_urlpatterns)
    ),
})
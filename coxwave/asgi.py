"""
ASGI config for coxwave project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import (
    ProtocolTypeRouter,
    URLRouter
)
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from chatbot.routing import chatbot_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(chatbot_urlpatterns)
            )
        ),
    }
)

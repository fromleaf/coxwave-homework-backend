from django.urls import path

from chatbot.consumers import ChatbotMessageConsumer

chatbot_urlpatterns = [
    path('ws/chat/', ChatbotMessageConsumer.as_asgi()),
]

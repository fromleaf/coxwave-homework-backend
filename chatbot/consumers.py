import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatbotMessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(
            text_data=json.dumps(
                {
                    "message": "WebSocket connection established!"
                }
            )
        )

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message = data.get('message', '')

        await self.send(
            text_data=json.dumps(
                {
                    "message": message
                }
            )
        )

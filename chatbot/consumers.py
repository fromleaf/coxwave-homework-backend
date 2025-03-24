import json

from channels.generic.websocket import AsyncWebsocketConsumer

from engine.engine_qa import get_naver_smartstore_qa_response


class ChatbotMessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        json_data = json.loads(text_data)
        question = json_data.get("question", None)
        context_history = json_data.get("context_history", [])

        message = get_naver_smartstore_qa_response(question, context_history)
        await self.send(
            text_data=json.dumps(
                {
                    "answer": message["answer"],
                    "suggestions": message["suggestions"]
                }
            )
        )

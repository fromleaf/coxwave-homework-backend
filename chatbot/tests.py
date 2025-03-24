import json

from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.test import TestCase
from django.urls import path

from chatbot.consumers import ChatbotMessageConsumer
from coxwave.const import messages

application = URLRouter(
    [
        path("ws/chat/", ChatbotMessageConsumer.as_asgi()),
    ]
)


class ChatbotMessageConsumerTests(TestCase):

    async def test_naver_smartstore_qa(self):
        communicator = WebsocketCommunicator(application, "/ws/chat/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        text_data = json.dumps(
            {
                "question": "미성년자도 판매 회원 등록이 가능한가요?"
            }
        )
        await communicator.send_to(text_data=text_data)
        response = await communicator.receive_from()

        response_json = json.loads(response)
        self.assertTrue(response_json["answer"] is not None)
        self.assertTrue(len(response_json["suggestions"]) > 0)

        print("Chatbot Response\n", response_json["answer"])
        print("\nSuggestions")
        for _idx, suggestion in enumerate(response_json["suggestions"], start=1):
            print(f"   - {suggestion}")

        await communicator.disconnect()

    async def test_naver_smartstore_qa_with_context_history(self):
        communicator = WebsocketCommunicator(application, "/ws/chat/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        questions = [
            "미성년자도 판매 회원 등록이 가능한가요?",
            "미성년자가 판매 가능한 제품은 어떤게 있을 까요?",
            "어떤 서류가 필요 할까요?",
        ]

        context_history = []
        for question in questions:
            text_data = json.dumps(
                {
                    "question": question,
                    "context_history": context_history
                }
            )
            await communicator.send_to(text_data=text_data)
            response = await communicator.receive_from()

            response_json = json.loads(response)
            self.assertTrue(response_json["answer"] is not None)
            self.assertTrue(len(response_json["suggestions"]) > 0)

            print("Question\n", question)
            print("\nChatbot Response\n", response_json["answer"])
            print("\nSuggestions")
            for _idx, suggestion in enumerate(response_json["suggestions"], start=1):
                print(f"   - {suggestion}")
            print("\n")

            context_history.append(f"{question}: {response_json['answer']}")

        await communicator.disconnect()

    async def test_not_relevant_message(self):
        test_input = "오늘 저녁에 여의도 가려는데 맛집 추천좀 해줄래?"
        expected_response = {
            "answer": messages.CHATBOT_NAVER_SMARTSTORE_ANSWER_FOR_NOT_RELEVANT_MESSAGE,
            "suggestions": []
        }

        communicator = WebsocketCommunicator(application, "/ws/chat/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_to(text_data=test_input)
        response = await communicator.receive_from()

        response_json = json.loads(response)
        self.assertEqual(response_json["answer"], expected_response["answer"])
        self.assertEqual(response_json["suggestions"], expected_response["suggestions"])

        print("Chatbot Response\n", response_json["answer"])
        print("\nSuggestions")
        for _idx, suggestion in enumerate(response_json["suggestions"], start=1):
            print(f"   - {suggestion}")

        await communicator.disconnect()

import json

from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.test import TestCase
from django.urls import path

from chatbot.consumers import ChatbotMessageConsumer
from coxwave import const
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

        question_data = {
            const.KEY_QUESTION: "미성년자도 판매 회원 등록이 가능한가요?"
        }
        text_data = json.dumps(question_data)
        await communicator.send_to(text_data=text_data)
        response = await communicator.receive_from()

        response_json = json.loads(response)
        self.assertTrue(response_json[const.KEY_ANSWER] is not None)
        self.assertTrue(len(response_json[const.KEY_SUGGESTIONS]) > 0)

        print("Question\n", question_data[const.KEY_QUESTION])
        print("\nChatbot Response\n", response_json[const.KEY_ANSWER])
        print("\nSuggestions")
        for _idx, suggestion in enumerate(response_json[const.KEY_SUGGESTIONS], start=1):
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
                    const.KEY_QUESTION: question,
                    const.KEY_CONTEXT_HISTORY: context_history
                }
            )
            await communicator.send_to(text_data=text_data)
            response = await communicator.receive_from()

            response_json = json.loads(response)
            self.assertTrue(response_json[const.KEY_ANSWER] is not None)
            self.assertTrue(len(response_json[const.KEY_SUGGESTIONS]) > 0)

            print("Question\n", question)
            print("\nChatbot Response\n", response_json[const.KEY_ANSWER])
            print("\nSuggestions")
            for _idx, suggestion in enumerate(response_json[const.KEY_SUGGESTIONS], start=1):
                print(f"   - {suggestion}")
            print("\n")

            context_history.append(f"{question}: {response_json[const.KEY_ANSWER]}")

        await communicator.disconnect()

    async def test_not_relevant_message(self):
        expected_response = {
            const.KEY_ANSWER: messages.CHATBOT_NAVER_SMARTSTORE_ANSWER_FOR_NOT_RELEVANT_MESSAGE,
            const.KEY_SUGGESTIONS: []
        }

        communicator = WebsocketCommunicator(application, "/ws/chat/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        question_data = {
            const.KEY_QUESTION: "오늘 저녁에 여의도 가려는데 맛집 추천좀 해줄래?",
            const.KEY_CONTEXT_HISTORY: []
        }
        text_data = json.dumps(question_data)
        await communicator.send_to(text_data=text_data)
        response = await communicator.receive_from()

        response_json = json.loads(response)
        self.assertEqual(response_json[const.KEY_ANSWER], expected_response[const.KEY_ANSWER])
        self.assertEqual(response_json[const.KEY_SUGGESTIONS], expected_response[const.KEY_SUGGESTIONS])

        print("Question\n", question_data[const.KEY_QUESTION])
        print("\nChatbot Response\n", response_json[const.KEY_ANSWER])

        await communicator.disconnect()

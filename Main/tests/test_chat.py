from unittest.mock import patch

from django.test import TestCase

from Main.models import ChatMessage
from .utils import create_user_with_profile


class ChatApiTests(TestCase):
    def setUp(self):
        self.user = create_user_with_profile()
        self.client.login(username=self.user.username, password="pass1234")

    @patch("Main.views.llm")
    def test_chat_api_creates_message(self, mock_llm):
        mock_llm.return_value = "Hello!"
        response = self.client.post("/api/chat/", data={"message": "Hi"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ChatMessage.objects.filter(user=self.user).exists())

    def test_chat_api_empty_message(self):
        response = self.client.post("/api/chat/", data={"message": ""})
        self.assertEqual(response.status_code, 400)

    @patch("Main.views.llm")
    def test_chat_api_coerces_non_string_response(self, mock_llm):
        mock_llm.return_value = {"response": "Structured hello"}
        response = self.client.post("/api/chat/", data={"message": "Hi"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["response"], "Structured hello")


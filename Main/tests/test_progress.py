from datetime import date

from django.test import TestCase

from Main.models import DailyProgress
from .utils import create_user_with_profile


class ProgressApiTests(TestCase):
    def setUp(self):
        self.user = create_user_with_profile()
        self.client.login(username=self.user.username, password="pass1234")

    def test_progress_update_api(self):
        response = self.client.post(
            "/api/progress/update/",
            data='{"date":"2025-01-01","workout_status":"done","nutrition_status":"hit"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(DailyProgress.objects.filter(user=self.user).exists())

    def test_progress_note_api(self):
        response = self.client.post(
            "/api/progress/note/",
            data='{"date":"2025-01-02","notes":"Felt good"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        entry = DailyProgress.objects.get(user=self.user, date=date(2025, 1, 2))
        self.assertEqual(entry.notes, "Felt good")

    def test_progress_invalid_date_returns_400(self):
        response = self.client.post(
            "/api/progress/update/",
            data='{"date":"bad-date"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)


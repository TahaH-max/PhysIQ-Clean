from django.test import TestCase

from .utils import create_user_with_profile


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = create_user_with_profile()
        self.client.login(username=self.user.username, password="pass1234")

    def test_overview_view(self):
        response = self.client.get("/dashboard/overview/")
        self.assertEqual(response.status_code, 200)

    def test_photo_locker_view(self):
        response = self.client.get("/dashboard/photo-locker/")
        self.assertEqual(response.status_code, 200)

    def test_community_feed_view(self):
        response = self.client.get("/dashboard/community-feed/")
        self.assertEqual(response.status_code, 200)


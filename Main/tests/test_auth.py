from django.contrib.messages import get_messages
from django.test import TestCase

from Main.models import UserProfile
from .utils import create_user_with_profile


class AuthAndMiddlewareTests(TestCase):
    def test_auth_page_loads(self):
        response = self.client.get("/auth/")
        self.assertEqual(response.status_code, 200)

    def test_register_page_loads(self):
        response = self.client.get("/auth/register/")
        self.assertEqual(response.status_code, 200)

    def test_register_redirects_to_dashboard(self):
        response = self.client.post(
            "/auth/register/",
            data={
                "username": "newuser",
                "email": "new@example.com",
                "password1": "pass1234",
                "password2": "pass1234",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/dashboard/")

    def test_dashboard_requires_login(self):
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/auth/"))

    def test_profile_redirect_when_incomplete(self):
        user = create_user_with_profile(complete_profile=False)
        self.client.login(username=user.username, password="pass1234")
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/profile/")

    def test_api_not_blocked_by_profile_middleware(self):
        user = create_user_with_profile(complete_profile=False)
        self.client.login(username=user.username, password="pass1234")
        response = self.client.post(
            "/api/progress/update/",
            data='{"date":"2025-01-01","workout_status":"done","nutrition_status":"hit"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_profile_post_saves_schedule(self):
        user = create_user_with_profile(complete_profile=False)
        self.client.login(username=user.username, password="pass1234")
        response = self.client.post(
            "/profile/",
            data={
                "age": 20,
                "height": "5'10",
                "weight": "170",
                "gender": "male",
                "fitness_goal": "maintain",
                "activity_level": "moderate",
                "dietary_preferences": "",
                "allergies": "",
                "budget": "",
                "schedule": '{"monday":["8-10"]}',
            },
        )
        self.assertEqual(response.status_code, 302)
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.schedule, {"monday": ["8-10"]})

    def test_photo_locker_requires_image(self):
        user = create_user_with_profile()
        self.client.login(username=user.username, password="pass1234")
        response = self.client.post("/dashboard/photo-locker/", data={})
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("select an image" in str(m).lower() for m in messages))


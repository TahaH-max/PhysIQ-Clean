"""Request middleware to enforce profile completion."""

from django.shortcuts import redirect
from django.urls import resolve
from django.urls.exceptions import Resolver404

from Main.models import UserProfile


class ForceProfileCompletionMiddleware:
    """Redirect authenticated users to finish their profile before using the app."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Short-circuit requests when profile completion is required."""
        if request.user.is_authenticated:
            profile, created = UserProfile.objects.get_or_create(
                user=request.user, defaults={"profile_completed": False}
            )

            # Skip profile enforcement for API routes and unresolved paths.
            if request.path_info.startswith("/api/"):
                return self.get_response(request)

            try:
                current_url = resolve(request.path_info).url_name
            except Resolver404:
                return self.get_response(request)

            # Allow profile page & logout while incomplete
            if not profile.profile_completed:
                if current_url not in ("profile", "logout"):
                    return redirect("profile")

        return self.get_response(request)


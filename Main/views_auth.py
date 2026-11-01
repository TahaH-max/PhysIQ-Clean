"""Authentication and profile views."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth import login

from .forms import LoginForm, RegisterForm, UserProfileForm
from .models import UserProfile


def login_view(request):
    """Render login form and authenticate the user."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    login_form = LoginForm(request, data=request.POST or None)

    if request.method == "POST":
        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Invalid username or password.")

    return render(
        request,
        "auth/login.html",
        {
            "login_form": login_form,
        },
    )


def register_view(request):
    """Render registration form and create a new account."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    register_form = RegisterForm(request.POST or None)

    if request.method == "POST":
        if register_form.is_valid():
            user = register_form.save()
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Please correct the errors below.")

    return render(
        request,
        "auth/register.html",
        {
            "register_form": register_form,
        },
    )


def logout_view(request):
    """Sign the user out and return to the landing page."""
    logout(request)
    return redirect("/")


@login_required
def profile_view(request):
    """Collect required profile data before unlocking the dashboard."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()

            profile.profile_completed = profile.is_complete()
            profile.save()

            return redirect("dashboard")
    else:
        form = UserProfileForm(instance=profile)

    return render(request, "auth/profile.html", {"form": form})


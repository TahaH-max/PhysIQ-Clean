"""Top-level dashboard entry view."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard_view(request):
    """Render the dashboard container; partials load dynamically."""
    return render(request, "dashboard/main.html")


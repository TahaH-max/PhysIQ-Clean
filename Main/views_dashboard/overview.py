"""Overview tab view and coach banner generation."""

import json
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import render
from django.utils import timezone

from Main.models import Plan, PhotoLocker
from Main.plan_utils import (
    find_today_block,
    serialize_nutrition_plan,
    serialize_workout_plan,
)
from prompts import generate_coach_summary


@login_required
def overview_view(request):
    """Assemble today's summary, coach banner, and overview context."""
    now_local = timezone.localtime()
    weekday_name = now_local.strftime("%A")

    try:
        # Linux / macOS use %-d (day without leading zero)
        pretty_date = now_local.strftime("%A, %b %-d")
    except ValueError:
        # Windows fallback uses %#d instead
        pretty_date = now_local.strftime("%A, %b %#d")

    latest_workout = (
        Plan.objects.filter(user=request.user, plan_type="workout")
        .order_by("-created_at")
        .first()
    )
    latest_nutrition = (
        Plan.objects.filter(user=request.user, plan_type="nutrition")
        .order_by("-created_at")
        .first()
    )

    workout_today = None
    nutrition_today = None
    daily_target = None
    macro_targets = {"protein_g": None, "carbs_g": None, "fat_g": None}
    meals_json = "[]"

    if latest_workout:
        workout_plan = serialize_workout_plan(latest_workout)
        week_plan = workout_plan.get("week_plan", [])
        workout_today = find_today_block(week_plan, weekday_name)

    if latest_nutrition:
        ndata = serialize_nutrition_plan(latest_nutrition)

        week_plan = ndata.get("week_plan", [])
        nutrition_today = find_today_block(week_plan, weekday_name)

        daily_targets = ndata.get("daily_targets", {})
        daily_target = daily_targets.get("calorie_target")

        macro_targets = {
            "protein_g": daily_targets.get("protein_g"),
            "carbs_g": daily_targets.get("carbs_g"),
            "fat_g": daily_targets.get("fat_g"),
        }

        if nutrition_today:
            try:
                meals_json = json.dumps(nutrition_today.get("meals", []))
            except Exception:
                meals_json = "[]"

    # Cache banner copy per user per day to avoid extra model calls.
    cache_key = f"coach_summary:{request.user.id}:{now_local.date()}"
    coach_banner = cache.get(cache_key)

    if not coach_banner:
        coach_banner = "Focus on consistency today — progress compounds."
        try:
            coach_banner = generate_coach_summary(
                request.user.username,
                workout_today,
                nutrition_today,
                {
                    "protein": macro_targets.get("protein_g"),
                    "carbs": macro_targets.get("carbs_g"),
                    "fat": macro_targets.get("fat_g"),
                    "calories": daily_target,
                },
            )
        except Exception:
            pass

        tomorrow = now_local + timezone.timedelta(days=1)
        midnight = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_until_midnight = int((midnight - now_local).total_seconds())

        cache.set(cache_key, coach_banner, timeout=seconds_until_midnight)

    today = timezone.localdate()
    new_posts_today = PhotoLocker.objects.filter(
        visibility="public", uploaded_at__date=today
    ).count()

    return render(
        request,
        "dashboard/partials/overview.html",
        {
            "today_str": pretty_date,
            "coach_banner": coach_banner,
            "workout_today": workout_today,
            "nutrition_today": nutrition_today,
            "nutrition_meals_json": meals_json,
            "macro_targets": macro_targets,
            "daily_calorie_target": daily_target,
            "view_name": "Overview",
            "new_posts_today": new_posts_today,
        },
    )


"""Progress tracking views and API endpoints."""

import json
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from Main.models import DailyProgress


def calculate_streaks(user):
    """Calculate current and best streaks for workout, nutrition, and overall."""
    today = timezone.localtime().date()

    entries = DailyProgress.objects.filter(user=user).order_by("-date")
    progress_dict = {e.date: e for e in entries}

    workout_current = 0
    workout_best = 0
    nutrition_current = 0
    nutrition_best = 0
    overall_current = 0
    overall_best = 0

    current_date = today
    while current_date in progress_dict:
        entry = progress_dict[current_date]
        if entry.workout_status == "done":
            workout_current += 1
            current_date -= timedelta(days=1)
        else:
            break

    current_date = today
    while current_date in progress_dict:
        entry = progress_dict[current_date]
        if entry.nutrition_status == "hit":
            nutrition_current += 1
            current_date -= timedelta(days=1)
        else:
            break

    current_date = today
    while current_date in progress_dict:
        entry = progress_dict[current_date]
        if entry.workout_status == "done" and entry.nutrition_status == "hit":
            overall_current += 1
            current_date -= timedelta(days=1)
        else:
            break

    start_date = today - timedelta(days=365)
    current_date = start_date

    workout_temp = 0
    nutrition_temp = 0
    overall_temp = 0

    while current_date <= today:
        entry = progress_dict.get(current_date)

        if entry and entry.workout_status == "done":
            workout_temp += 1
            workout_best = max(workout_best, workout_temp)
        else:
            workout_temp = 0

        if entry and entry.nutrition_status == "hit":
            nutrition_temp += 1
            nutrition_best = max(nutrition_best, nutrition_temp)
        else:
            nutrition_temp = 0

        if entry and entry.workout_status == "done" and entry.nutrition_status == "hit":
            overall_temp += 1
            overall_best = max(overall_best, overall_temp)
        else:
            overall_temp = 0

        current_date += timedelta(days=1)

    workout_best = max(workout_best, workout_current)
    nutrition_best = max(nutrition_best, nutrition_current)
    overall_best = max(overall_best, overall_current)

    return {
        "workout_current": workout_current,
        "workout_best": workout_best,
        "nutrition_current": nutrition_current,
        "nutrition_best": nutrition_best,
        "overall_current": overall_current,
        "overall_best": overall_best,
    }


@login_required
def progress_view(request):
    """Render the progress dashboard for the current week."""
    today = timezone.localtime().date()

    week_start = today - timedelta(days=today.weekday())
    week_dates = [week_start + timedelta(days=i) for i in range(7)]

    progress_data = []
    # Precompute a row for each day of the week, even if no entry exists.
    for date in week_dates:
        try:
            entry = DailyProgress.objects.get(user=request.user, date=date)
            progress_data.append(
                {
                    "date": date,
                    "day_name": date.strftime("%a"),
                    "day_num": date.day,
                    "workout_status": entry.workout_status,
                    "nutrition_status": entry.nutrition_status,
                    "notes": entry.notes,
                    "is_today": date == today,
                }
            )
        except DailyProgress.DoesNotExist:
            progress_data.append(
                {
                    "date": date,
                    "day_name": date.strftime("%a"),
                    "day_num": date.day,
                    "workout_status": "missed",
                    "nutrition_status": "none",
                    "notes": "",
                    "is_today": date == today,
                }
            )

    streaks = calculate_streaks(request.user)

    return render(
        request,
        "dashboard/partials/progress.html",
        {
            "view_name": "Progress",
            "week_data": progress_data,
            "streaks": streaks,
        },
    )


@login_required
@require_http_methods(["POST"])
def update_progress(request):
    """Create or update daily workout/nutrition statuses."""
    try:
        data = json.loads(request.body)
        date_str = data.get("date")
        workout_status = data.get("workout_status")
        nutrition_status = data.get("nutrition_status")

        if not date_str:
            return JsonResponse({"error": "Date is required"}, status=400)

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"error": "Invalid date format."}, status=400)

        entry, created = DailyProgress.objects.get_or_create(
            user=request.user,
            date=date,
            defaults={
                "workout_status": workout_status or "missed",
                "nutrition_status": nutrition_status or "none",
            },
        )

        if not created:
            if workout_status:
                entry.workout_status = workout_status
            if nutrition_status:
                entry.nutrition_status = nutrition_status
            entry.save()

        streaks = calculate_streaks(request.user)

        return JsonResponse(
            {
                "success": True,
                "workout_status": entry.workout_status,
                "nutrition_status": entry.nutrition_status,
                "streaks": streaks,
            }
        )

    except Exception:
        return JsonResponse({"error": "Failed to update progress."}, status=500)


@login_required
@require_http_methods(["POST"])
def save_progress_note(request):
    """Create or update progress notes for a given day."""
    try:
        data = json.loads(request.body)
        date_str = data.get("date")
        notes = data.get("notes", "")

        if not date_str:
            return JsonResponse({"error": "Date is required"}, status=400)

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"error": "Invalid date format."}, status=400)

        entry, created = DailyProgress.objects.get_or_create(
            user=request.user, date=date, defaults={"notes": notes}
        )

        if not created:
            entry.notes = notes
            entry.save()

        return JsonResponse(
            {
                "success": True,
                "notes": entry.notes,
            }
        )

    except Exception:
        return JsonResponse({"error": "Failed to save note."}, status=500)


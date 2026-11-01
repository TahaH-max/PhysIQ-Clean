"""Workout plan view and regeneration handler."""

import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from Main.models import UserProfile, Plan
from Main.plan_utils import (
    create_workout_plan_from_json,
    serialize_workout_plan,
    validate_workout_plan,
)
from prompts import build_workout_prompt, WORKOUT_SYSTEM_MESSAGE
from wrappers.azure_chat import llm

logger = logging.getLogger(__name__)


@login_required
def workout_view(request):
    """Render workout planner and handle plan regeneration requests."""
    # Ensure profile exists; middleware may not have created one yet.
    user, _ = UserProfile.objects.get_or_create(user=request.user)

    latest_plan = (
        Plan.objects.filter(user=request.user, plan_type="workout")
        .order_by("-created_at")
        .first()
    )
    invalid_request = False

    if request.method == "POST":
        goal = ""
        schedule = ""
        notes = ""
        if request.headers.get("Content-Type", "").startswith("application/json"):
            try:
                data = json.loads(request.body.decode("utf-8"))
                goal = data.get("goal", "")
                schedule = data.get("schedule", "")
                notes = data.get("notes", "")
            except json.JSONDecodeError:
                logger.warning("Workout update received invalid JSON.")
                invalid_request = True
                messages.error(request, "Invalid request format.")

        if not invalid_request:
            user_prompt = build_workout_prompt(
                user_profile=user, current_goal=goal, schedule=schedule, notes=notes
            )
            response_json = llm(user_prompt, system_message=WORKOUT_SYSTEM_MESSAGE)

            valid, error = validate_workout_plan(response_json)
            if valid:
                latest_plan = create_workout_plan_from_json(
                    request.user, response_json, raw_response=response_json
                )
            else:
                # Keep the previous plan and surface a friendly error.
                logger.warning("Workout plan validation failed: %s", error)
                messages.error(
                    request, "We couldn't generate a valid workout plan. Please try again."
                )

    # First-time visitors get an auto-generated plan (unless request was invalid).
    if not latest_plan and not invalid_request:
        user_prompt = build_workout_prompt(
            user_profile=user, current_goal="", schedule="", notes=""
        )
        response_json = llm(user_prompt, system_message=WORKOUT_SYSTEM_MESSAGE)
        valid, error = validate_workout_plan(response_json)
        if valid:
            latest_plan = create_workout_plan_from_json(
                request.user, response_json, raw_response=response_json
            )
        else:
            logger.warning("Initial workout plan validation failed: %s", error)

    plan_data = serialize_workout_plan(latest_plan) if latest_plan else {"week_plan": []}

    return render(
        request,
        "dashboard/partials/workout.html",
        {"plan": plan_data, "view_name": "Workout Planner"},
    )


"""Nutrition plan view and regeneration handler."""

import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from Main.models import UserProfile, Plan
from Main.plan_utils import (
    create_nutrition_plan_from_json,
    serialize_nutrition_plan,
    validate_nutrition_plan,
)
from prompts import build_nutrition_prompt, NUTRITION_SYSTEM_MESSAGE
from wrappers.azure_chat import llm

logger = logging.getLogger(__name__)


@login_required
def nutrition_view(request):
    """Render nutrition planner and handle plan regeneration requests."""
    user, _ = UserProfile.objects.get_or_create(user=request.user)
    latest_plan = (
        Plan.objects.filter(user=request.user, plan_type="nutrition")
        .order_by("-created_at")
        .first()
    )

    if request.method == "POST":
        user_prompt = build_nutrition_prompt(
            user_profile=user, current_goal="", notes=""
        )
        response_json = llm(user_prompt, system_message=NUTRITION_SYSTEM_MESSAGE)
        valid, error = validate_nutrition_plan(response_json)
        if valid:
            latest_plan = create_nutrition_plan_from_json(
                request.user, response_json, raw_response=response_json
            )
        else:
            logger.warning("Nutrition plan validation failed: %s", error)
            messages.error(
                request,
                "We couldn't generate a valid nutrition plan. Please try again.",
            )

    # Generate a baseline plan for first-time visitors.
    if not latest_plan:
        user_prompt = build_nutrition_prompt(
            user_profile=user, current_goal="", notes=""
        )
        response_json = llm(user_prompt, system_message=NUTRITION_SYSTEM_MESSAGE)
        valid, error = validate_nutrition_plan(response_json)
        if valid:
            latest_plan = create_nutrition_plan_from_json(
                request.user, response_json, raw_response=response_json
            )
        else:
            logger.warning("Initial nutrition plan validation failed: %s", error)

    plan = serialize_nutrition_plan(latest_plan) if latest_plan else {
        "daily_targets": {
            "calorie_target": 0,
            "protein_g": 0,
            "carbs_g": 0,
            "fat_g": 0,
        },
        "week_plan": [],
        "encouragement_message": "We couldn't load a plan yet. Please try regenerating.",
    }

    for day in plan["week_plan"]:
        day["meals_json"] = json.dumps(day["meals"])

    return render(
        request,
        "dashboard/partials/nutrition.html",
        {"plan": plan, "view_name": "Nutrition Planner"},
    )


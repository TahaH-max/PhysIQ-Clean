"""Utilities for validating, persisting, and serializing AI plans."""

from django.db import transaction

from .models import (
    DAY_ORDER,
    Plan,
    WorkoutDay,
    WorkoutExercise,
    NutritionDay,
    Meal,
    MealItem,
)

DAY_NAME_MAP = {day.lower(): day for day in DAY_ORDER}


def _to_int(value):
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_day_name(value):
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    return DAY_NAME_MAP.get(normalized.lower())


def find_today_block(week_plan, weekday_name):
    """Find a day block by name, defaulting to the first entry when missing."""
    if not week_plan:
        return None
    for day in week_plan:
        if str(day.get("day", "")).strip().lower() == weekday_name.strip().lower():
            return day
    return week_plan[0]


def validate_workout_plan(plan):
    """Lightweight validation to avoid saving unusable workout plans."""
    if not isinstance(plan, dict):
        return False, "Workout plan is not a JSON object."
    week_plan = plan.get("week_plan")
    if not isinstance(week_plan, list) or len(week_plan) != 7:
        return False, "Workout plan must include 7 days."
    seen_days = set()
    for day in week_plan:
        if not isinstance(day, dict):
            return False, "Workout day must be an object."
        day_name_raw = day.get("day")
        if not day_name_raw or not day.get("session_type"):
            return False, "Workout day missing required fields."
        day_name = _normalize_day_name(day_name_raw)
        if not day_name:
            return False, "Workout plan has an invalid day name."
        if day_name in seen_days:
            return False, "Workout plan has duplicate days."
        seen_days.add(day_name)
        if "recommended_time" not in day:
            return False, "Workout day missing recommended_time."
    return True, ""


def validate_nutrition_plan(plan):
    """Lightweight validation to avoid saving unusable nutrition plans."""
    if not isinstance(plan, dict):
        return False, "Nutrition plan is not a JSON object."
    if not isinstance(plan.get("daily_targets"), dict):
        return False, "Nutrition plan missing daily targets."
    week_plan = plan.get("week_plan")
    if not isinstance(week_plan, list) or len(week_plan) != 7:
        return False, "Nutrition plan must include 7 days."
    seen_days = set()
    for day in week_plan:
        if not isinstance(day, dict):
            return False, "Nutrition day must be an object."
        day_name_raw = day.get("day")
        if not day_name_raw:
            return False, "Nutrition day missing day name."
        day_name = _normalize_day_name(day_name_raw)
        if not day_name:
            return False, "Nutrition plan has an invalid day name."
        if day_name in seen_days:
            return False, "Nutrition plan has duplicate days."
        seen_days.add(day_name)
        if not isinstance(day.get("meals"), list):
            return False, "Nutrition day missing meals."
    return True, ""


def create_workout_plan_from_json(user, response_json, raw_response=None):
    """Persist a workout plan response into normalized tables."""
    week_plan = response_json.get("week_plan", []) if isinstance(response_json, dict) else []
    encouragement = ""
    if isinstance(response_json, dict):
        encouragement = response_json.get("encouragement_message") or ""

    with transaction.atomic():
        plan = Plan.objects.create(
            user=user,
            plan_type="workout",
            encouragement_message=encouragement,
            raw_response=raw_response or response_json,
        )

        for day_index, day in enumerate(week_plan):
            day_name = _normalize_day_name(day.get("day")) or ""
            workout_day = WorkoutDay.objects.create(
                plan=plan,
                day=day_name,
                recommended_time=day.get("recommended_time", ""),
                focus=day.get("focus", ""),
                session_type=day.get("session_type", ""),
                notes=day.get("notes", ""),
                sort_order=day_index,
            )

            for ex_index, ex in enumerate(day.get("exercises", []) or []):
                WorkoutExercise.objects.create(
                    workout_day=workout_day,
                    name=ex.get("name", ""),
                    sets=_to_int(ex.get("sets")),
                    reps=_to_int(ex.get("reps")),
                    distance_m=_to_float(ex.get("distance_m")),
                    notes=ex.get("notes", ""),
                    sort_order=ex_index,
                )

    return plan


def create_nutrition_plan_from_json(user, response_json, raw_response=None):
    """Persist a nutrition plan response into normalized tables."""
    daily_targets = response_json.get("daily_targets", {}) if isinstance(response_json, dict) else {}
    week_plan = response_json.get("week_plan", []) if isinstance(response_json, dict) else []
    encouragement = ""
    if isinstance(response_json, dict):
        encouragement = response_json.get("encouragement_message") or ""

    with transaction.atomic():
        plan = Plan.objects.create(
            user=user,
            plan_type="nutrition",
            encouragement_message=encouragement,
            calorie_target=_to_float(daily_targets.get("calorie_target")),
            protein_g=_to_float(daily_targets.get("protein_g")),
            carbs_g=_to_float(daily_targets.get("carbs_g")),
            fat_g=_to_float(daily_targets.get("fat_g")),
            raw_response=raw_response or response_json,
        )

        for day_index, day in enumerate(week_plan):
            day_name = _normalize_day_name(day.get("day")) or ""
            nutrition_day = NutritionDay.objects.create(
                plan=plan,
                day=day_name,
                notes=day.get("notes", ""),
                day_total_calories=_to_float(day.get("day_total_calories")),
                sort_order=day_index,
            )

            for meal_index, meal in enumerate(day.get("meals", []) or []):
                meal_obj = Meal.objects.create(
                    nutrition_day=nutrition_day,
                    name=meal.get("name", ""),
                    meal_total_calories=_to_float(meal.get("meal_total_calories")),
                    sort_order=meal_index,
                )

                for item_index, item in enumerate(meal.get("items", []) or []):
                    MealItem.objects.create(
                        meal=meal_obj,
                        food=item.get("food", ""),
                        portion=item.get("portion", ""),
                        calories=_to_float(item.get("calories")),
                        protein_g=_to_float(item.get("protein_g")),
                        carbs_g=_to_float(item.get("carbs_g")),
                        fat_g=_to_float(item.get("fat_g")),
                        notes=item.get("notes", ""),
                        sort_order=item_index,
                    )

    return plan


def serialize_workout_plan(plan):
    """Convert a workout plan and related data into the legacy dict shape."""
    if not plan:
        return {"week_plan": [], "encouragement_message": ""}

    week_plan = []
    for day in plan.workout_days.all():
        exercises = []
        for ex in day.exercises.all():
            exercises.append(
                {
                    "name": ex.name,
                    "sets": ex.sets,
                    "reps": ex.reps,
                    "distance_m": ex.distance_m,
                    "notes": ex.notes,
                }
            )

        week_plan.append(
            {
                "day": day.day,
                "recommended_time": day.recommended_time,
                "focus": day.focus,
                "session_type": day.session_type,
                "exercises": exercises,
                "notes": day.notes,
            }
        )

    return {
        "week_plan": week_plan,
        "encouragement_message": plan.encouragement_message or "",
    }


def serialize_nutrition_plan(plan):
    """Convert a nutrition plan and related data into the legacy dict shape."""
    if not plan:
        return {
            "daily_targets": {
                "calorie_target": 0,
                "protein_g": 0,
                "carbs_g": 0,
                "fat_g": 0,
            },
            "week_plan": [],
            "encouragement_message": "",
        }

    week_plan = []
    for day in plan.nutrition_days.all():
        meals = []
        for meal in day.meals.all():
            items = []
            for item in meal.items.all():
                items.append(
                    {
                        "food": item.food,
                        "portion": item.portion,
                        "calories": item.calories,
                        "protein_g": item.protein_g,
                        "carbs_g": item.carbs_g,
                        "fat_g": item.fat_g,
                        "notes": item.notes,
                    }
                )

            meals.append(
                {
                    "name": meal.name,
                    "items": items,
                    "meal_total_calories": meal.meal_total_calories,
                }
            )

        week_plan.append(
            {
                "day": day.day,
                "meals": meals,
                "day_total_calories": day.day_total_calories,
                "notes": day.notes,
            }
        )

    return {
        "daily_targets": {
            "calorie_target": plan.calorie_target or 0,
            "protein_g": plan.protein_g or 0,
            "carbs_g": plan.carbs_g or 0,
            "fat_g": plan.fat_g or 0,
        },
        "week_plan": week_plan,
        "encouragement_message": plan.encouragement_message or "",
    }


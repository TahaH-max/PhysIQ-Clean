from unittest.mock import patch

from django.test import TestCase

from Main.models import (
    Meal,
    MealItem,
    NutritionDay,
    Plan,
    WorkoutDay,
    WorkoutExercise,
)
from Main.plan_utils import validate_nutrition_plan, validate_workout_plan
from .utils import create_user_with_profile


class PlanViewTests(TestCase):
    def setUp(self):
        self.user = create_user_with_profile()
        self.client.login(username=self.user.username, password="pass1234")

    @patch("Main.views_dashboard.workout.llm")
    def test_workout_view_creates_plan(self, mock_llm):
        mock_llm.return_value = {
            "week_plan": [
                {
                    "day": "Monday",
                    "recommended_time": "6:00 AM - 7:00 AM",
                    "focus": "Push",
                    "session_type": "Workout",
                    "exercises": [
                        {"name": "Bench Press", "sets": 4, "reps": 8, "distance_m": None, "notes": ""},
                        {"name": "Incline Dumbbell Press", "sets": 3, "reps": 10, "distance_m": None, "notes": ""},
                    ],
                    "notes": "",
                },
                {
                    "day": "Tuesday",
                    "recommended_time": "6:00 AM - 7:00 AM",
                    "focus": "Cardio",
                    "session_type": "Cardio",
                    "exercises": [
                        {"name": "Treadmill", "sets": None, "reps": None, "distance_m": 2000, "notes": "Easy pace"},
                    ],
                    "notes": "",
                },
                {
                    "day": "Wednesday",
                    "recommended_time": "Flexible",
                    "focus": "Rest",
                    "session_type": "Rest",
                    "exercises": [],
                    "notes": "Recover",
                },
                {
                    "day": "Thursday",
                    "recommended_time": "6:00 AM - 7:00 AM",
                    "focus": "Pull",
                    "session_type": "Workout",
                    "exercises": [
                        {"name": "Barbell Row", "sets": 4, "reps": 8, "distance_m": None, "notes": ""},
                    ],
                    "notes": "",
                },
                {
                    "day": "Friday",
                    "recommended_time": "6:00 AM - 7:00 AM",
                    "focus": "Legs",
                    "session_type": "Workout",
                    "exercises": [
                        {"name": "Back Squat", "sets": 4, "reps": 6, "distance_m": None, "notes": ""},
                    ],
                    "notes": "",
                },
                {
                    "day": "Saturday",
                    "recommended_time": "Flexible",
                    "focus": "Rest",
                    "session_type": "Rest",
                    "exercises": [],
                    "notes": "Recover",
                },
                {
                    "day": "Sunday",
                    "recommended_time": "Flexible",
                    "focus": "Rest",
                    "session_type": "Rest",
                    "exercises": [],
                    "notes": "Recover",
                },
            ],
            "encouragement_message": "You got this!",
        }
        response = self.client.get("/dashboard/workout/")
        self.assertEqual(response.status_code, 200)
        plan = Plan.objects.filter(user=self.user, plan_type="workout").first()
        self.assertIsNotNone(plan)
        self.assertEqual(WorkoutDay.objects.filter(plan=plan).count(), 7)
        self.assertGreater(WorkoutExercise.objects.filter(workout_day__plan=plan).count(), 0)

    @patch("Main.views_dashboard.nutrition.llm")
    def test_nutrition_view_creates_plan(self, mock_llm):
        mock_llm.return_value = {
            "daily_targets": {"calorie_target": 2000, "protein_g": 150, "carbs_g": 200, "fat_g": 60},
            "week_plan": [
                {
                    "day": "Monday",
                    "meals": [
                        {
                            "name": "Breakfast",
                            "items": [
                                {
                                    "food": "Greek yogurt",
                                    "portion": "1 cup",
                                    "calories": 150,
                                    "protein_g": 20,
                                    "carbs_g": 10,
                                    "fat_g": 2,
                                    "notes": "",
                                }
                            ],
                            "meal_total_calories": 150,
                        },
                        {
                            "name": "Lunch",
                            "items": [
                                {
                                    "food": "Chicken breast",
                                    "portion": "150g",
                                    "calories": 250,
                                    "protein_g": 40,
                                    "carbs_g": 0,
                                    "fat_g": 5,
                                    "notes": "",
                                }
                            ],
                            "meal_total_calories": 250,
                        },
                        {
                            "name": "Dinner",
                            "items": [
                                {
                                    "food": "Salmon",
                                    "portion": "150g",
                                    "calories": 280,
                                    "protein_g": 30,
                                    "carbs_g": 0,
                                    "fat_g": 15,
                                    "notes": "",
                                }
                            ],
                            "meal_total_calories": 280,
                        },
                        {
                            "name": "Snack",
                            "items": [
                                {
                                    "food": "Apple",
                                    "portion": "1 medium",
                                    "calories": 95,
                                    "protein_g": 0,
                                    "carbs_g": 25,
                                    "fat_g": 0,
                                    "notes": "",
                                }
                            ],
                            "meal_total_calories": 95,
                        },
                    ],
                    "day_total_calories": 2000,
                    "notes": "",
                },
                {"day": "Tuesday", "meals": [], "day_total_calories": 2000, "notes": ""},
                {"day": "Wednesday", "meals": [], "day_total_calories": 2000, "notes": ""},
                {"day": "Thursday", "meals": [], "day_total_calories": 2000, "notes": ""},
                {"day": "Friday", "meals": [], "day_total_calories": 2000, "notes": ""},
                {"day": "Saturday", "meals": [], "day_total_calories": 2000, "notes": ""},
                {"day": "Sunday", "meals": [], "day_total_calories": 2000, "notes": ""},
            ],
            "encouragement_message": "Great job!",
        }
        response = self.client.get("/dashboard/nutrition/")
        self.assertEqual(response.status_code, 200)
        plan = Plan.objects.filter(user=self.user, plan_type="nutrition").first()
        self.assertIsNotNone(plan)
        self.assertEqual(NutritionDay.objects.filter(plan=plan).count(), 7)
        self.assertGreater(Meal.objects.filter(nutrition_day__plan=plan).count(), 0)
        self.assertGreater(MealItem.objects.filter(meal__nutrition_day__plan=plan).count(), 0)

    def test_workout_invalid_json_does_not_create_plan(self):
        existing = Plan.objects.filter(user=self.user, plan_type="workout").count()
        response = self.client.post(
            "/dashboard/workout/",
            data="{bad json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Plan.objects.filter(user=self.user, plan_type="workout").count(), existing)

    def test_workout_plan_validation_rejects_duplicate_day(self):
        valid, error = validate_workout_plan(
            {
                "week_plan": [
                    {"day": "Monday", "recommended_time": "6:00 AM - 7:00 AM", "focus": "Push", "session_type": "Workout", "exercises": [], "notes": ""},
                    {"day": "Monday", "recommended_time": "6:00 AM - 7:00 AM", "focus": "Pull", "session_type": "Workout", "exercises": [], "notes": ""},
                    {"day": "Wednesday", "recommended_time": "Flexible", "focus": "Rest", "session_type": "Rest", "exercises": [], "notes": "Recover"},
                    {"day": "Thursday", "recommended_time": "6:00 AM - 7:00 AM", "focus": "Pull", "session_type": "Workout", "exercises": [], "notes": ""},
                    {"day": "Friday", "recommended_time": "6:00 AM - 7:00 AM", "focus": "Legs", "session_type": "Workout", "exercises": [], "notes": ""},
                    {"day": "Saturday", "recommended_time": "Flexible", "focus": "Rest", "session_type": "Rest", "exercises": [], "notes": "Recover"},
                    {"day": "Sunday", "recommended_time": "Flexible", "focus": "Rest", "session_type": "Rest", "exercises": [], "notes": "Recover"},
                ],
                "encouragement_message": "You got this!",
            }
        )
        self.assertFalse(valid)
        self.assertIn("duplicate", error.lower())

    def test_workout_plan_validation_rejects_non_string_day(self):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        week_plan = [
            {
                "day": day,
                "recommended_time": "6:00 AM - 7:00 AM",
                "focus": "Workout",
                "session_type": "Workout",
                "exercises": [],
                "notes": "",
            }
            for day in days
        ]
        week_plan[0]["day"] = ["Monday"]
        valid, error = validate_workout_plan(
            {"week_plan": week_plan, "encouragement_message": "You got this!"}
        )
        self.assertFalse(valid)
        self.assertIn("invalid", error.lower())

    def test_nutrition_plan_validation_rejects_invalid_day(self):
        valid, error = validate_nutrition_plan(
            {
                "daily_targets": {"calorie_target": 2000, "protein_g": 150, "carbs_g": 200, "fat_g": 60},
                "week_plan": [
                    {"day": "Monday", "meals": [], "day_total_calories": 2000, "notes": ""},
                    {"day": "Tuesday", "meals": [], "day_total_calories": 2000, "notes": ""},
                    {"day": "Wednesday", "meals": [], "day_total_calories": 2000, "notes": ""},
                    {"day": "Thursday", "meals": [], "day_total_calories": 2000, "notes": ""},
                    {"day": "Friday", "meals": [], "day_total_calories": 2000, "notes": ""},
                    {"day": "Saturday", "meals": [], "day_total_calories": 2000, "notes": ""},
                    {"day": "Funday", "meals": [], "day_total_calories": 2000, "notes": ""},
                ],
                "encouragement_message": "Great job!",
            }
        )
        self.assertFalse(valid)
        self.assertIn("invalid", error.lower())

    def test_nutrition_plan_validation_accepts_lowercase_days(self):
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        week_plan = [
            {"day": day, "meals": [], "day_total_calories": 2000, "notes": ""}
            for day in days
        ]
        valid, error = validate_nutrition_plan(
            {
                "daily_targets": {"calorie_target": 2000, "protein_g": 150, "carbs_g": 200, "fat_g": 60},
                "week_plan": week_plan,
                "encouragement_message": "Great job!",
            }
        )
        self.assertTrue(valid)
        self.assertEqual(error, "")


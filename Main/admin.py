"""Admin registrations for core models."""

from django.contrib import admin

from .models import (
    UserProfile,
    Plan,
    ChatMessage,
    DailyProgress,
    PhotoLocker,
    WorkoutDay,
    WorkoutExercise,
    NutritionDay,
    Meal,
    MealItem,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for user profiles."""
    list_display = ("user", "age", "gender", "fitness_goal", "profile_completed")
    search_fields = ("user__username", "user__email")
    list_filter = ("gender", "activity_level", "profile_completed")


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """Admin configuration for saved plans."""
    list_display = ("user", "plan_type", "created_at")
    list_filter = ("plan_type",)
    search_fields = ("user__username",)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin configuration for chat history."""
    list_display = ("user", "timestamp")
    search_fields = ("user__username", "message")
    list_filter = ("timestamp",)


@admin.register(DailyProgress)
class DailyProgressAdmin(admin.ModelAdmin):
    """Admin configuration for daily progress entries."""
    list_display = ("user", "date", "workout_status", "nutrition_status")
    list_filter = ("workout_status", "nutrition_status")
    search_fields = ("user__username",)


@admin.register(PhotoLocker)
class PhotoLockerAdmin(admin.ModelAdmin):
    """Admin configuration for photo locker entries."""
    list_display = ("user", "visibility", "uploaded_at")
    list_filter = ("visibility", "uploaded_at")
    search_fields = ("user__username", "note")


@admin.register(WorkoutDay)
class WorkoutDayAdmin(admin.ModelAdmin):
    list_display = ("plan", "day", "session_type", "focus", "recommended_time")
    list_filter = ("session_type", "focus")
    search_fields = ("plan__user__username", "day")


@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ("workout_day", "name", "sets", "reps", "distance_m")
    search_fields = ("workout_day__plan__user__username", "name")


@admin.register(NutritionDay)
class NutritionDayAdmin(admin.ModelAdmin):
    list_display = ("plan", "day", "day_total_calories")
    search_fields = ("plan__user__username", "day")


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ("nutrition_day", "name", "meal_total_calories")
    search_fields = ("nutrition_day__plan__user__username", "name")


@admin.register(MealItem)
class MealItemAdmin(admin.ModelAdmin):
    list_display = ("meal", "food", "calories", "protein_g", "carbs_g", "fat_g")
    search_fields = ("meal__nutrition_day__plan__user__username", "food")


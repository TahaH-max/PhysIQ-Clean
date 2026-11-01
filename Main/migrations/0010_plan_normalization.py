from django.db import migrations, models
import django.db.models.deletion


DAY_CHOICES = [
    ("Monday", "Monday"),
    ("Tuesday", "Tuesday"),
    ("Wednesday", "Wednesday"),
    ("Thursday", "Thursday"),
    ("Friday", "Friday"),
    ("Saturday", "Saturday"),
    ("Sunday", "Sunday"),
]

MEAL_CHOICES = [
    ("Breakfast", "Breakfast"),
    ("Lunch", "Lunch"),
    ("Dinner", "Dinner"),
    ("Snack", "Snack"),
]


class Migration(migrations.Migration):

    dependencies = [
        ("Main", "0009_photolocker"),
    ]

    operations = [
        migrations.AddField(
            model_name="plan",
            name="encouragement_message",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="plan",
            name="calorie_target",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="plan",
            name="protein_g",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="plan",
            name="carbs_g",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="plan",
            name="fat_g",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="plan",
            name="raw_response",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.RemoveField(
            model_name="plan",
            name="plan_data",
        ),
        migrations.CreateModel(
            name="WorkoutDay",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("day", models.CharField(choices=DAY_CHOICES, max_length=12)),
                (
                    "recommended_time",
                    models.CharField(blank=True, default="", max_length=50),
                ),
                ("focus", models.CharField(blank=True, default="", max_length=30)),
                (
                    "session_type",
                    models.CharField(blank=True, default="", max_length=30),
                ),
                ("notes", models.TextField(blank=True, default="")),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                (
                    "plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="workout_days",
                        to="Main.plan",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order", "id"],
                "unique_together": {("plan", "day")},
            },
        ),
        migrations.CreateModel(
            name="WorkoutExercise",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("sets", models.IntegerField(blank=True, null=True)),
                ("reps", models.IntegerField(blank=True, null=True)),
                ("distance_m", models.FloatField(blank=True, null=True)),
                ("notes", models.TextField(blank=True, default="")),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                (
                    "workout_day",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="exercises",
                        to="Main.workoutday",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order", "id"],
            },
        ),
        migrations.CreateModel(
            name="NutritionDay",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("day", models.CharField(choices=DAY_CHOICES, max_length=12)),
                ("notes", models.TextField(blank=True, default="")),
                ("day_total_calories", models.FloatField(blank=True, null=True)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                (
                    "plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="nutrition_days",
                        to="Main.plan",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order", "id"],
                "unique_together": {("plan", "day")},
            },
        ),
        migrations.CreateModel(
            name="Meal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(choices=MEAL_CHOICES, max_length=20)),
                ("meal_total_calories", models.FloatField(blank=True, null=True)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                (
                    "nutrition_day",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="meals",
                        to="Main.nutritionday",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order", "id"],
            },
        ),
        migrations.CreateModel(
            name="MealItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("food", models.CharField(max_length=200)),
                ("portion", models.CharField(max_length=100)),
                ("calories", models.FloatField(blank=True, null=True)),
                ("protein_g", models.FloatField(blank=True, null=True)),
                ("carbs_g", models.FloatField(blank=True, null=True)),
                ("fat_g", models.FloatField(blank=True, null=True)),
                ("notes", models.TextField(blank=True, default="")),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                (
                    "meal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="Main.meal",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order", "id"],
            },
        ),
    ]


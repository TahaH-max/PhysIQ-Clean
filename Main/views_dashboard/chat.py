"""Chat tab view and prompt suggestions."""

import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from Main.models import ChatMessage


@login_required
def chat_view(request):
    """Render chat history and prompt suggestions for the coach bot."""
    prompt_suggestions = [
        "What are some effective exercises for building muscle?",
        "How can I improve my cardio endurance?",
        "What should I eat before a workout?",
        "Can you suggest a 30-minute home workout?",
        "How do I stay motivated to exercise regularly?",
        "What are good post-workout meals?",
        "How many calories should I eat to lose weight?",
        "What's the best way to track my fitness progress?",
        "How can I avoid workout injuries?",
        "What supplements do you recommend?",
        "How do I build a balanced meal plan?",
        "What are some healthy snack options?",
    ]

    # Shuffle a few starter prompts to keep the chat tab fresh.
    selected_prompts = random.sample(
        prompt_suggestions, min(5, len(prompt_suggestions))
    )

    chat_history = ChatMessage.objects.filter(user=request.user)[:50]

    return render(
        request,
        "dashboard/partials/chat.html",
        {
            "view_name": "Coach Bot",
            "prompt_suggestions": selected_prompts,
            "chat_history": reversed(list(chat_history)),
        },
    )


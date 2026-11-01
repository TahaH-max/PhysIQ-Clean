"""Dashboard view package to keep feature views isolated and maintainable."""

from .dashboard import dashboard_view
from .overview import overview_view
from .workout import workout_view
from .nutrition import nutrition_view
from .progress import progress_view, update_progress, save_progress_note
from .chat import chat_view
from .photos import photo_locker_view, community_feed_view, photo_image_view

__all__ = [
    "dashboard_view",
    "overview_view",
    "workout_view",
    "nutrition_view",
    "progress_view",
    "update_progress",
    "save_progress_note",
    "chat_view",
    "photo_locker_view",
    "community_feed_view",
    "photo_image_view",
]


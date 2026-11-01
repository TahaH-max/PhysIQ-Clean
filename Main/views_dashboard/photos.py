"""Photo locker and community feed views."""

import mimetypes

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect
from django.conf import settings
from PIL import Image, UnidentifiedImageError

from Main.models import PhotoLocker


ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}


def _validate_uploaded_image(image):
    """Return an error message for invalid uploads, otherwise None."""
    max_size = getattr(settings, "MAX_UPLOAD_SIZE_BYTES", 5 * 1024 * 1024)

    if image.size > max_size:
        max_mb = max_size // (1024 * 1024)
        return f"Image must be under {max_mb}MB."

    content_type = image.content_type or mimetypes.guess_type(image.name)[0]
    if content_type not in ALLOWED_IMAGE_MIME_TYPES:
        return "Unsupported image type. Please upload a JPG, PNG, WEBP, or GIF."

    try:
        Image.open(image).verify()
    except (UnidentifiedImageError, OSError):
        return "Uploaded file is not a valid image."
    finally:
        image.seek(0)

    return None


@login_required
def photo_locker_view(request):
    """Allow users to upload and review their progress photos."""
    photos = PhotoLocker.objects.filter(user=request.user).order_by("-uploaded_at")

    if request.method == "POST":
        image = request.FILES.get("image")
        if not image:
            messages.error(request, "Please select an image to upload.")
            return redirect("photo_locker")

        error = _validate_uploaded_image(image)
        if error:
            messages.error(request, error)
            return redirect("photo_locker")

        note = request.POST.get("note", "").strip()
        visibility = request.POST.get("visibility", "private")

        PhotoLocker.objects.create(
            user=request.user, image=image, note=note, visibility=visibility
        )

        return redirect("/dashboard/?tab=photo-locker")

    return render(
        request,
        "dashboard/partials/photo_locker.html",
        {"photos": photos, "view_name": "Photo Locker"},
    )


@login_required
def community_feed_view(request):
    """Show all public photos in the community feed."""
    posts = PhotoLocker.public_photos()
    return render(
        request,
        "dashboard/partials/community_feed.html",
        {"posts": posts, "view_name": "Community Feed"},
    )


def photo_image_view(request, photo_id):
    """Serve images only to the owner or the public feed."""
    try:
        photo = PhotoLocker.objects.select_related("user").get(pk=photo_id)
    except PhotoLocker.DoesNotExist as exc:
        raise Http404("Photo not found.") from exc

    if photo.visibility != "public":
        if not request.user.is_authenticated or photo.user_id != request.user.id:
            raise Http404("Photo not found.")

    if not photo.image:
        raise Http404("Photo not found.")

    content_type, _ = mimetypes.guess_type(photo.image.name)
    response = FileResponse(photo.image.open("rb"), content_type=content_type)
    response["Content-Length"] = photo.image.size
    return response


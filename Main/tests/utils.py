from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from Main.models import UserProfile


def create_user_with_profile(username="tester", password="pass1234", complete_profile=True):
    user = User.objects.create_user(username=username, password=password)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    if complete_profile:
        profile.profile_completed = True
        profile.age = 20
        profile.height = "5'10"
        profile.weight = "170"
        profile.fitness_goal = "maintain"
        profile.save()
    return user


def create_test_image(filename="test.jpg", size=(32, 32), image_format="JPEG"):
    image_bytes = BytesIO()
    image = Image.new("RGB", size=size, color=(255, 0, 0))
    image.save(image_bytes, format=image_format)
    image_bytes.seek(0)
    return SimpleUploadedFile(
        filename, image_bytes.read(), content_type="image/jpeg"
    )


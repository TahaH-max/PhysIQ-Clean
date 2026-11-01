import shutil
import tempfile

from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from Main.models import PhotoLocker
from .utils import create_user_with_profile, create_test_image


class PhotoSecurityTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.settings_override = self.settings(MEDIA_ROOT=self.media_root)
        self.settings_override.enable()

        self.owner = create_user_with_profile(username="owner")
        self.other = create_user_with_profile(username="other")

    def tearDown(self):
        self.settings_override.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)

    def test_private_photo_requires_owner(self):
        photo = PhotoLocker.objects.create(
            user=self.owner,
            image=create_test_image(),
            visibility="private",
        )

        self.client.login(username=self.other.username, password="pass1234")
        response = self.client.get(f"/media/photo/{photo.id}/")
        self.assertEqual(response.status_code, 404)

        self.client.login(username=self.owner.username, password="pass1234")
        response = self.client.get(f"/media/photo/{photo.id}/")
        self.assertEqual(response.status_code, 200)

    def test_public_photo_accessible_without_login(self):
        photo = PhotoLocker.objects.create(
            user=self.owner,
            image=create_test_image(),
            visibility="public",
        )

        response = self.client.get(f"/media/photo/{photo.id}/")
        self.assertEqual(response.status_code, 200)

    def test_private_photo_404_when_logged_out(self):
        photo = PhotoLocker.objects.create(
            user=self.owner,
            image=create_test_image(),
            visibility="private",
        )

        response = self.client.get(f"/media/photo/{photo.id}/")
        self.assertEqual(response.status_code, 404)

    def test_photo_upload_rejects_non_image(self):
        self.client.login(username=self.owner.username, password="pass1234")
        bad_file = SimpleUploadedFile(
            "bad.txt", b"not an image", content_type="text/plain"
        )
        response = self.client.post(
            "/dashboard/photo-locker/", data={"image": bad_file}
        )
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("unsupported image type" in str(m).lower() for m in messages))


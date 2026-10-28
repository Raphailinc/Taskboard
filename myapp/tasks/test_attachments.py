import tempfile
from datetime import date
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import Task, TaskFile


class AttachmentAccessTests(TestCase):
    def setUp(self):
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        settings = override_settings(MEDIA_ROOT=self.media.name)
        settings.enable()
        self.addCleanup(settings.disable)
        self.owner = get_user_model().objects.create_user(username="owner")
        self.other = get_user_model().objects.create_user(username="other")
        self.task = Task.objects.create(title="Private task", assigned_to=self.owner)
        self.attachment = TaskFile.objects.create(
            task=self.task,
            file=SimpleUploadedFile("notes.txt", b"private attachment"),
        )
        self.client.force_login(self.owner)

    def test_owner_can_download_attachment(self):
        response = self.client.get(reverse("view_file", args=[self.attachment.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), b"private attachment")
        self.assertIn("attachment;", response["Content-Disposition"])
        response.close()

    def test_other_account_cannot_download_or_delete_attachment(self):
        self.client.force_login(self.other)
        for route, method in [("view_file", "get"), ("delete_file", "post")]:
            with self.subTest(route=route):
                response = getattr(self.client, method)(reverse(route, args=[self.attachment.id]))
                self.assertEqual(response.status_code, 404)
        self.assertTrue(TaskFile.objects.filter(pk=self.attachment.pk).exists())
        self.assertTrue(Path(self.attachment.file.path).exists())

    def test_get_cannot_delete_attachment(self):
        response = self.client.get(reverse("delete_file", args=[self.attachment.id]))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(TaskFile.objects.filter(pk=self.attachment.pk).exists())

    def test_delete_requires_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        response = client.post(reverse("delete_file", args=[self.attachment.id]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(TaskFile.objects.filter(pk=self.attachment.pk).exists())

    def test_owner_can_delete_attachment(self):
        path = Path(self.attachment.file.path)
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(reverse("delete_file", args=[self.attachment.id]))
        self.assertRedirects(response, reverse("task_detail", args=[self.task.id]))
        self.assertFalse(TaskFile.objects.filter(pk=self.attachment.pk).exists())
        self.assertFalse(path.exists())

    def test_task_deletion_cleans_up_its_attachments(self):
        path = Path(self.attachment.file.path)
        with self.captureOnCommitCallbacks(execute=True):
            self.task.delete()
        self.assertFalse(path.exists())

    def test_rolled_back_deletion_preserves_attachment(self):
        path = Path(self.attachment.file.path)
        attachment_id = self.attachment.pk
        with self.captureOnCommitCallbacks(execute=True):
            with self.assertRaises(RuntimeError):
                with transaction.atomic():
                    self.attachment.delete()
                    raise RuntimeError("roll back deletion")
        self.assertTrue(TaskFile.objects.filter(pk=attachment_id).exists())
        self.assertTrue(path.exists())

    @override_settings(DEBUG=True)
    def test_raw_media_url_does_not_expose_private_attachment(self):
        self.client.logout()
        response = self.client.get(self.attachment.file.url)
        self.assertEqual(response.status_code, 404)

    def test_detail_uses_protected_download_url(self):
        response = self.client.get(reverse("task_detail", args=[self.task.id]))
        self.assertContains(response, reverse("view_file", args=[self.attachment.id]))
        self.assertNotContains(response, self.attachment.file.url)

    def test_missing_storage_file_returns_404(self):
        Path(self.attachment.file.path).unlink()
        response = self.client.get(reverse("view_file", args=[self.attachment.id]))
        self.assertEqual(response.status_code, 404)

    def test_equal_deadlines_sort_high_priority_first(self):
        self.task.delete()
        for priority in ["low", "high", "medium"]:
            Task.objects.create(
                title=priority,
                priority=priority,
                due_date=date(2030, 1, 1),
                assigned_to=self.owner,
            )
        response = self.client.get(reverse("task_list"))
        self.assertEqual(
            [task.priority for task in response.context["tasks"]],
            ["high", "medium", "low"],
        )

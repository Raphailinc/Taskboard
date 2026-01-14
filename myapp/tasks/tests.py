from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Task


class TaskTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.task = Task.objects.create(title='Test Task', description='This is a test task', assigned_to=self.user)

    def test_task_list_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')

    def test_task_detail_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('task_detail', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')

    def test_task_create_view(self):
        self.client.login(username='testuser', password='testpassword')
        data = {
            "title": "New Task",
            "description": "Desc",
            "priority": "high",
            "status": "todo",
        }
        response = self.client.post(reverse('task_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='New Task').exists())

    def test_task_delete_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('task_delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(title='Test Task').exists())

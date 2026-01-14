from django import forms
from .models import Task, TaskFile


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "priority", "status", "due_date"]
        labels = {
            "title": "Заголовок",
            "description": "Описание",
            "priority": "Приоритет",
            "status": "Статус",
            "due_date": "Дедлайн",
        }
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }


class TaskFileForm(forms.ModelForm):
    class Meta:
        model = TaskFile
        fields = ["file"]

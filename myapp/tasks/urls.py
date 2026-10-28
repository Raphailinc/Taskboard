from django.urls import path

from .views import (
    delete_file,
    task_create,
    task_delete,
    task_detail,
    task_list,
    task_update,
    view_file,
)

urlpatterns = [
    path("tasks/", task_list, name="task_list"),
    path("tasks/<int:task_id>/", task_detail, name="task_detail"),
    path("tasks/create/", task_create, name="task_create"),
    path("tasks/<int:task_id>/update/", task_update, name="task_update"),
    path("tasks/<int:task_id>/delete/", task_delete, name="task_delete"),
    path("files/<int:file_id>/view/", view_file, name="view_file"),
    path("files/<int:file_id>/delete/", delete_file, name="delete_file"),
]

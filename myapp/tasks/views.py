import logging

from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Case, IntegerField, Q, Value, When
from django.http import FileResponse, Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import TaskFileForm, TaskForm
from .models import Task, TaskFile

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@login_required
def task_list(request):
    query = request.GET.get("q", "")
    status = request.GET.get("status")
    tasks = Task.objects.filter(assigned_to=request.user)

    if query:
        tasks = tasks.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if status:
        tasks = tasks.filter(status=status)

    tasks = tasks.annotate(
        priority_rank=Case(
            When(priority="high", then=Value(0)),
            When(priority="medium", then=Value(1)),
            default=Value(2),
            output_field=IntegerField(),
        )
    ).order_by("due_date", "priority_rank", "-created_at", "pk")

    page = request.GET.get("page", 1)
    paginator = Paginator(tasks, 10)
    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        tasks = paginator.page(paginator.num_pages)

    return render(request, "task_list.html", {"tasks": tasks, "query": query})


@login_required
def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_to = request.user
            task.save()
            return redirect("task_list")
    else:
        form = TaskForm()
    return render(request, "task_form.html", {"form": form})


@login_required
def task_update(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect("task_list")
    else:
        form = TaskForm(instance=task)
    return render(request, "task_form.html", {"form": form})


@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    if request.method == "POST":
        task.delete()
        return redirect("task_list")
    return HttpResponseBadRequest("Invalid method")


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    task_files = TaskFile.objects.filter(task=task)

    if request.method == "POST":
        file_form = TaskFileForm(request.POST, request.FILES)
        if file_form.is_valid():
            new_file = file_form.save(commit=False)
            new_file.task = task
            new_file.save()
            return redirect("task_detail", task_id=task.id)
    else:
        file_form = TaskFileForm()

    return render(
        request,
        "task_detail.html",
        {"task": task, "task_files": task_files, "file_form": file_form},
    )


@login_required
def view_file(request, file_id):
    task_file = get_object_or_404(TaskFile, id=file_id, task__assigned_to=request.user)

    try:
        attachment = task_file.file.open("rb")
    except FileNotFoundError as exc:
        raise Http404("Attachment is no longer available.") from exc
    return FileResponse(attachment, as_attachment=True)


@login_required
@require_POST
def delete_file(request, file_id):
    task_file = get_object_or_404(TaskFile, id=file_id, task__assigned_to=request.user)
    task_id = task_file.task.id
    task_file.delete()
    return redirect("task_detail", task_id=task_id)

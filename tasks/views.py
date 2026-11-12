from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from accounts.decorators import admin_or_pm_required
from .models import Task, Bug
from .forms import TaskForm, TaskStatusUpdateForm, BugReportForm, BugUpdateForm
from projects.models import Project

# -------------------------------------------------------------
# TASK MANAGEMENT VIEWS
# -------------------------------------------------------------

@login_required
def task_list_view(request):
    """
    Searchable and filterable tasks list.
    Developers view their assigned tasks. PMs monitor all project tasks.
    Highlights overdue tasks.
    """
    user = request.user
    tasks = Task.objects.select_related('project__client', 'assigned_developer__user', 'created_by').all()

    # Developer scoping: default to assigned tasks unless toggling all
    view_scope = request.GET.get('scope', '').strip()
    if user.is_dev_role and hasattr(user, 'employee_profile') and view_scope != 'all':
        tasks = tasks.filter(assigned_developer=user.employee_profile)

    # Search
    search_query = request.GET.get('q', '').strip()
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) |
            Q(task_id__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(project__name__icontains=search_query)
        )

    # Filter by Priority
    priority_filter = request.GET.get('priority', '').strip()
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    # Filter by Status
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    # Filter by Project
    project_filter = request.GET.get('project', '').strip()
    if project_filter:
        tasks = tasks.filter(project_id=project_filter)

    # Status counts for pipeline tabs
    if user.is_dev_role and hasattr(user, 'employee_profile') and view_scope != 'all':
        base_qs = Task.objects.filter(assigned_developer=user.employee_profile)
    else:
        base_qs = Task.objects.all()

    total_count = base_qs.count()
    todo_count = base_qs.filter(status=Task.Status.TODO).count()
    inprogress_count = base_qs.filter(status=Task.Status.IN_PROGRESS).count()
    completed_count = base_qs.filter(status=Task.Status.COMPLETED).count()
    blocked_count = base_qs.filter(status=Task.Status.BLOCKED).count()

    projects = Project.objects.all()
    priorities = Task.Priority.choices
    statuses = Task.Status.choices

    return render(request, 'tasks/task_list.html', {
        'tasks': tasks,
        'search_query': search_query,
        'priority_filter': priority_filter,
        'status_filter': status_filter,
        'project_filter': project_filter,
        'view_scope': view_scope,
        'projects': projects,
        'priorities': priorities,
        'statuses': statuses,
        'total_count': total_count,
        'todo_count': todo_count,
        'inprogress_count': inprogress_count,
        'completed_count': completed_count,
        'blocked_count': blocked_count,
        'page_title': 'Tasks & Sprints'
    })


@login_required
def task_detail_view(request, pk):
    """Detailed view of an individual task with status quick-transition actions."""
    task = get_object_or_404(
        Task.objects.select_related('project__client', 'assigned_developer__user', 'created_by'),
        pk=pk
    )

    can_edit = (
        request.user.is_admin_role or
        request.user.is_pm_role or
        (hasattr(request.user, 'employee_profile') and task.assigned_developer == request.user.employee_profile)
    )

    return render(request, 'tasks/task_detail.html', {
        'task': task,
        'can_edit': can_edit,
        'page_title': f'Task: {task.title}'
    })


@login_required
@admin_or_pm_required
def task_create_view(request):
    """Project Managers and Admins create tasks and allocate developers."""
    initial_data = {}
    project_id = request.GET.get('project')
    if project_id:
        initial_data['project'] = project_id

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, f"Task '{task.title}' ({task.task_id}) created successfully.")
            return redirect('tasks:detail', pk=task.pk)
        else:
            messages.error(request, "Please fix the errors in the task form.")
    else:
        form = TaskForm(initial=initial_data)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'action': 'Create',
        'page_title': 'Create New Task'
    })


@login_required
@admin_or_pm_required
def task_edit_view(request, pk):
    """Project Managers and Admins update task specifications or assignees."""
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f"Task '{task.title}' updated successfully.")
            return redirect('tasks:detail', pk=task.pk)
        else:
            messages.error(request, "Please resolve the form errors.")
    else:
        form = TaskForm(instance=task)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'action': 'Edit',
        'task': task,
        'page_title': f'Edit Task: {task.title}'
    })


@login_required
@admin_or_pm_required
def task_delete_view(request, pk):
    """Deletes a task record with confirmation."""
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        title = task.title
        task.delete()
        messages.success(request, f"Task '{title}' has been deleted.")
        return redirect('tasks:list')

    return render(request, 'tasks/task_confirm_delete.html', {
        'task': task,
        'page_title': f'Confirm Delete: {task.title}'
    })


@login_required
def task_status_update_view(request, pk):
    """
    Developer action to transition their assigned task status:
    (TODO -> IN_PROGRESS -> COMPLETED -> BLOCKED)
    """
    task = get_object_or_404(Task, pk=pk)

    # Permission check: must be assigned developer, PM, or Admin
    is_authorized = (
        request.user.is_admin_role or
        request.user.is_pm_role or
        (hasattr(request.user, 'employee_profile') and task.assigned_developer == request.user.employee_profile)
    )
    if not is_authorized:
        messages.error(request, "You are only permitted to update status for tasks assigned to you.")
        return redirect('tasks:list')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in Task.Status.values:
            task.status = new_status
            task.save()
            messages.success(request, f"Task status updated to '{task.get_status_display()}'.")
        else:
            messages.error(request, "Invalid status transition selected.")

    return redirect('tasks:detail', pk=task.pk)


# -------------------------------------------------------------
# BUG TRACKING VIEWS
# -------------------------------------------------------------

@login_required
def bug_list_view(request):
    """
    Searchable and filterable bug issues tracker.
    Filter by status and priority.
    """
    bugs = Bug.objects.select_related('project__client', 'reported_by', 'assigned_developer__user').all()

    # Search
    search_query = request.GET.get('q', '').strip()
    if search_query:
        bugs = bugs.filter(
            Q(title__icontains=search_query) |
            Q(bug_id__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(project__name__icontains=search_query)
        )

    # Filter by Priority
    priority_filter = request.GET.get('priority', '').strip()
    if priority_filter:
        bugs = bugs.filter(priority=priority_filter)

    # Filter by Status
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        bugs = bugs.filter(status=status_filter)

    # Filter by Project
    project_filter = request.GET.get('project', '').strip()
    if project_filter:
        bugs = bugs.filter(project_id=project_filter)

    # Status counts for pipeline tabs
    total_bugs = Bug.objects.count()
    open_count = Bug.objects.filter(status=Bug.Status.OPEN).count()
    inprogress_count = Bug.objects.filter(status=Bug.Status.IN_PROGRESS).count()
    resolved_count = Bug.objects.filter(status=Bug.Status.RESOLVED).count()
    closed_count = Bug.objects.filter(status=Bug.Status.CLOSED).count()

    projects = Project.objects.all()
    priorities = Bug.Priority.choices
    statuses = Bug.Status.choices

    return render(request, 'tasks/bug_list.html', {
        'bugs': bugs,
        'search_query': search_query,
        'priority_filter': priority_filter,
        'status_filter': status_filter,
        'project_filter': project_filter,
        'projects': projects,
        'priorities': priorities,
        'statuses': statuses,
        'total_bugs': total_bugs,
        'open_count': open_count,
        'inprogress_count': inprogress_count,
        'resolved_count': resolved_count,
        'closed_count': closed_count,
        'page_title': 'Bug Issues Tracker'
    })


@login_required
def bug_detail_view(request, pk):
    """Detailed view of reported bug defect, reproduction notes, and resolution history."""
    bug = get_object_or_404(
        Bug.objects.select_related('project__client', 'reported_by', 'assigned_developer__user'),
        pk=pk
    )

    can_edit = (
        request.user.is_admin_role or
        request.user.is_pm_role or
        (hasattr(request.user, 'employee_profile') and bug.assigned_developer == request.user.employee_profile) or
        bug.reported_by == request.user
    )

    return render(request, 'tasks/bug_detail.html', {
        'bug': bug,
        'can_edit': can_edit,
        'page_title': f'Bug: {bug.title}'
    })


@login_required
def bug_report_view(request):
    """Allows developers and team members to report a software bug against a project."""
    initial_data = {}
    project_id = request.GET.get('project')
    if project_id:
        initial_data['project'] = project_id

    if request.method == 'POST':
        form = BugReportForm(request.POST)
        if form.is_valid():
            bug = form.save(commit=False)
            bug.reported_by = request.user
            bug.status = Bug.Status.OPEN
            bug.save()
            messages.success(request, f"Bug report '{bug.title}' ({bug.bug_id}) submitted for project triage.")
            return redirect('tasks:bug_detail', pk=bug.pk)
        else:
            messages.error(request, "Please resolve the errors in the bug report.")
    else:
        form = BugReportForm(initial=initial_data)

    return render(request, 'tasks/bug_form.html', {
        'form': form,
        'action': 'Report',
        'page_title': 'Report Software Bug'
    })


@login_required
def bug_edit_view(request, pk):
    """PMs assign bugs to developers, and developers update bug resolution notes and status."""
    bug = get_object_or_404(Bug, pk=pk)

    if request.method == 'POST':
        form = BugUpdateForm(request.POST, instance=bug)
        if form.is_valid():
            form.save()
            messages.success(request, f"Bug issue '{bug.title}' updated successfully.")
            return redirect('tasks:bug_detail', pk=bug.pk)
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = BugUpdateForm(instance=bug)

    return render(request, 'tasks/bug_form.html', {
        'form': form,
        'action': 'Update',
        'bug': bug,
        'page_title': f'Triage Bug: {bug.title}'
    })


@login_required
@admin_or_pm_required
def bug_delete_view(request, pk):
    """Deletes a bug issue with confirmation."""
    bug = get_object_or_404(Bug, pk=pk)

    if request.method == 'POST':
        title = bug.title
        bug.delete()
        messages.success(request, f"Bug report '{title}' has been removed.")
        return redirect('tasks:bug_list')

    return render(request, 'tasks/bug_confirm_delete.html', {
        'bug': bug,
        'page_title': f'Confirm Delete: {bug.title}'
    })

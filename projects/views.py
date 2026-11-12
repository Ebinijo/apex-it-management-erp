from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from accounts.decorators import admin_or_pm_required
from .models import Project
from .forms import ProjectForm

@login_required
def project_list_view(request):
    """
    Searchable and filterable project portfolio directory.
    Search by project name, ID, client, or PM. Filter by status.
    """
    user = request.user
    projects = Project.objects.select_related('client', 'project_manager__user').prefetch_related('team_members__user').all()

    # Search
    search_query = request.GET.get('q', '').strip()
    if search_query:
        projects = projects.filter(
            Q(name__icontains=search_query) |
            Q(project_id__icontains=search_query) |
            Q(client__company_name__icontains=search_query) |
            Q(project_manager__user__first_name__icontains=search_query) |
            Q(project_manager__user__last_name__icontains=search_query)
        )

    # Filter by Status
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        projects = projects.filter(status=status_filter)

    # Filter for Developer's or PM's Assigned Projects
    scope_filter = request.GET.get('scope', '').strip()
    if scope_filter == 'my_projects' and hasattr(user, 'employee_profile'):
        profile = user.employee_profile
        projects = projects.filter(Q(team_members=profile) | Q(project_manager=profile)).distinct()

    statuses = Project.Status.choices

    # Project status summary counters
    total_projects = Project.objects.count()
    ongoing_count = Project.objects.filter(status=Project.Status.IN_PROGRESS).count()
    testing_count = Project.objects.filter(status=Project.Status.TESTING).count()
    completed_count = Project.objects.filter(status=Project.Status.COMPLETED).count()

    return render(request, 'projects/project_list.html', {
        'projects': projects,
        'search_query': search_query,
        'status_filter': status_filter,
        'scope_filter': scope_filter,
        'statuses': statuses,
        'total_projects': total_projects,
        'ongoing_count': ongoing_count,
        'testing_count': testing_count,
        'completed_count': completed_count,
        'page_title': 'Engineering Projects Portfolio'
    })


@login_required
def project_detail_view(request, pk):
    """
    Detailed Project View containing:
    - Overview & Client Information
    - Project Manager & Team Members
    - Deadline & Overdue calculation
    - Progress Bar (completed_tasks / total_tasks * 100)
    - Tasks & Bugs summaries
    """
    project = get_object_or_404(
        Project.objects.select_related('client', 'project_manager__user').prefetch_related('team_members__user', 'team_members__department'),
        pk=pk
    )

    # Check developer assignment if viewing restricted projects
    is_authorized = (
        request.user.is_admin_role or
        request.user.is_hr_role or
        (hasattr(request.user, 'employee_profile') and (
            project.project_manager == request.user.employee_profile or
            project.team_members.filter(pk=request.user.employee_profile.pk).exists()
        ))
    )

    # In Phase 5, tasks and bugs will be queried here:
    tasks = project.tasks.select_related('assigned_developer__user').all() if hasattr(project, 'tasks') else []
    bugs = project.bugs.select_related('assigned_developer__user', 'reported_by').all() if hasattr(project, 'bugs') else []

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'tasks': tasks,
        'bugs': bugs,
        'is_authorized': is_authorized,
        'page_title': f'Project: {project.name}'
    })


@login_required
@admin_or_pm_required
def project_create_view(request):
    """Admin and Project Manager view to initialize a new project."""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, f"Project '{project.name}' ({project.project_id}) created successfully.")
            return redirect('projects:detail', pk=project.pk)
        else:
            messages.error(request, "Please correct the errors in the project form.")
    else:
        form = ProjectForm()

    return render(request, 'projects/project_form.html', {
        'form': form,
        'action': 'Create',
        'page_title': 'Initialize New Software Project'
    })


@login_required
@admin_or_pm_required
def project_edit_view(request, pk):
    """Admin and Project Manager view to update project scope, status, or team."""
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f"Project '{project.name}' updated successfully.")
            return redirect('projects:detail', pk=project.pk)
        else:
            messages.error(request, "Please resolve the highlighted errors.")
    else:
        form = ProjectForm(instance=project)

    return render(request, 'projects/project_form.html', {
        'form': form,
        'action': 'Edit',
        'project': project,
        'page_title': f'Edit Project: {project.name}'
    })


@login_required
@admin_or_pm_required
def project_delete_view(request, pk):
    """Admin and Project Manager view to delete project with confirmation."""
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        name = project.name
        project.delete()
        messages.success(request, f"Project '{name}' has been deleted.")
        return redirect('projects:list')

    return render(request, 'projects/project_confirm_delete.html', {
        'project': project,
        'page_title': f'Confirm Delete: {project.name}'
    })

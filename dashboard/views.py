from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from accounts.models import User
from accounts.decorators import admin_required, hr_required, pm_required, dev_required
from employees.models import EmployeeProfile, Department, LeaveRequest
from clients.models import Client, Lead
from projects.models import Project
from tasks.models import Task, Bug

@login_required
def index(request):
    """
    Main entry point for authenticated users.
    Dispatches to role-specific dashboard views.
    """
    user = request.user
    if user.is_superuser or user.role == User.Role.ADMIN:
        return redirect('dashboard:admin')
    elif user.role == User.Role.HR:
        return redirect('dashboard:hr')
    elif user.role == User.Role.PROJECT_MANAGER:
        return redirect('dashboard:pm')
    elif user.role == User.Role.DEVELOPER:
        return redirect('dashboard:developer')
    return redirect('accounts:profile')


@admin_required
def admin_dashboard_view(request):
    """Admin Dashboard showing high-level company metrics."""
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    admins_count = User.objects.filter(role=User.Role.ADMIN).count()
    hrs_count = User.objects.filter(role=User.Role.HR).count()
    pms_count = User.objects.filter(role=User.Role.PROJECT_MANAGER).count()
    devs_count = User.objects.filter(role=User.Role.DEVELOPER).count()

    total_employees = EmployeeProfile.objects.count()
    pending_leaves = LeaveRequest.objects.filter(status=LeaveRequest.Status.PENDING).count()

    total_clients = Client.objects.count()
    total_leads = Lead.objects.count()

    leads_new = Lead.objects.filter(status=Lead.Status.NEW).count()
    leads_contacted = Lead.objects.filter(status=Lead.Status.CONTACTED).count()
    leads_converted = Lead.objects.filter(status=Lead.Status.CONVERTED).count()
    leads_lost = Lead.objects.filter(status=Lead.Status.LOST).count()

    total_projects = Project.objects.count()
    ongoing_projects = Project.objects.filter(status=Project.Status.IN_PROGRESS).count()
    completed_projects = Project.objects.filter(status=Project.Status.COMPLETED).count()
    proj_planning = Project.objects.filter(status=Project.Status.PLANNING).count()
    proj_testing = Project.objects.filter(status=Project.Status.TESTING).count()
    proj_on_hold = Project.objects.filter(status=Project.Status.ON_HOLD).count()

    total_tasks = Task.objects.count()
    pending_tasks = Task.objects.exclude(status=Task.Status.COMPLETED).count()
    completed_tasks = Task.objects.filter(status=Task.Status.COMPLETED).count()
    open_bugs = Bug.objects.filter(status__in=[Bug.Status.OPEN, Bug.Status.IN_PROGRESS]).count()

    task_todo = Task.objects.filter(status=Task.Status.TODO).count()
    task_inprogress = Task.objects.filter(status=Task.Status.IN_PROGRESS).count()
    task_completed = completed_tasks
    task_blocked = Task.objects.filter(status=Task.Status.BLOCKED).count()

    # Department distribution
    departments_data = Department.objects.annotate(emp_count=Count('employees')).order_by('-emp_count')
    dept_names = [d.name for d in departments_data]
    dept_counts = [d.emp_count for d in departments_data]

    context = {
        'page_title': 'Executive Admin Dashboard',
        'total_users': total_users,
        'active_users': active_users,
        'admins_count': admins_count,
        'hrs_count': hrs_count,
        'pms_count': pms_count,
        'devs_count': devs_count,
        'total_employees': total_employees,
        'pending_leaves': pending_leaves,
        'total_clients': total_clients,
        'total_leads': total_leads,
        'leads_new': leads_new,
        'leads_contacted': leads_contacted,
        'leads_converted': leads_converted,
        'leads_lost': leads_lost,
        'total_projects': total_projects,
        'ongoing_projects': ongoing_projects,
        'completed_projects': completed_projects,
        'proj_planning': proj_planning,
        'proj_testing': proj_testing,
        'proj_on_hold': proj_on_hold,
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'open_bugs': open_bugs,
        'task_todo': task_todo,
        'task_inprogress': task_inprogress,
        'task_completed': task_completed,
        'task_blocked': task_blocked,
        'dept_names': dept_names,
        'dept_counts': dept_counts,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@hr_required
def hr_dashboard_view(request):
    """HR Dashboard focusing on employees, headcount, and leave requests."""
    total_employees = EmployeeProfile.objects.count()
    active_employees = EmployeeProfile.objects.exclude(
        employment_status=EmployeeProfile.EmploymentStatus.RESIGNED
    ).count()

    pending_leaves = LeaveRequest.objects.filter(status=LeaveRequest.Status.PENDING).count()
    approved_leaves = LeaveRequest.objects.filter(status=LeaveRequest.Status.APPROVED).count()
    rejected_leaves = LeaveRequest.objects.filter(status=LeaveRequest.Status.REJECTED).count()

    # Department breakdown with counts
    departments_data = Department.objects.annotate(emp_count=Count('employees')).order_by('-emp_count')
    dept_names = [d.name for d in departments_data]
    dept_counts = [d.emp_count for d in departments_data]

    # Recent pending leaves queue
    pending_leaves_queue = LeaveRequest.objects.filter(
        status=LeaveRequest.Status.PENDING
    ).select_related('employee__user')[:5]

    context = {
        'page_title': 'HR Management Dashboard',
        'total_employees': total_employees,
        'active_employees': active_employees,
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
        'rejected_leaves': rejected_leaves,
        'departments_data': departments_data,
        'dept_names': dept_names,
        'dept_counts': dept_counts,
        'pending_leaves_queue': pending_leaves_queue,
    }
    return render(request, 'dashboard/hr_dashboard.html', context)


@pm_required
def pm_dashboard_view(request):
    """Project Manager Dashboard displaying managed projects, task velocity, and bugs."""
    user = request.user
    today = timezone.now().date()
    try:
        pm_profile = user.employee_profile
        managed_projects = Project.objects.filter(project_manager=pm_profile).select_related('client')
        pm_tasks = Task.objects.filter(project__in=managed_projects).select_related('project', 'assigned_developer__user')
        pm_bugs = Bug.objects.filter(project__in=managed_projects).select_related('project', 'assigned_developer__user')
    except Exception:
        managed_projects = Project.objects.all().select_related('client')
        pm_tasks = Task.objects.all().select_related('project', 'assigned_developer__user')
        pm_bugs = Bug.objects.all().select_related('project', 'assigned_developer__user')

    assigned_projects_count = managed_projects.count()
    ongoing_projects_count = managed_projects.filter(status=Project.Status.IN_PROGRESS).count()
    completed_projects_count = managed_projects.filter(status=Project.Status.COMPLETED).count()

    total_tasks_count = pm_tasks.count()
    pending_tasks_count = pm_tasks.exclude(status=Task.Status.COMPLETED).count()
    overdue_tasks_count = pm_tasks.filter(deadline__lt=today).exclude(status=Task.Status.COMPLETED).count()
    open_bugs_count = pm_bugs.filter(status__in=[Bug.Status.OPEN, Bug.Status.IN_PROGRESS]).count()
    recent_tasks = pm_tasks.order_by('-created_at')[:5]
    recent_bugs = pm_bugs.order_by('-created_at')[:5]

    pm_tasks_todo = pm_tasks.filter(status=Task.Status.TODO).count()
    pm_tasks_inprogress = pm_tasks.filter(status=Task.Status.IN_PROGRESS).count()
    pm_tasks_completed = pm_tasks.filter(status=Task.Status.COMPLETED).count()
    pm_tasks_blocked = pm_tasks.filter(status=Task.Status.BLOCKED).count()

    context = {
        'page_title': 'Project Manager Operations Dashboard',
        'managed_projects': managed_projects,
        'assigned_projects_count': assigned_projects_count,
        'ongoing_projects_count': ongoing_projects_count,
        'completed_projects_count': completed_projects_count,
        'total_tasks_count': total_tasks_count,
        'pending_tasks_count': pending_tasks_count,
        'overdue_tasks_count': overdue_tasks_count,
        'open_bugs_count': open_bugs_count,
        'recent_tasks': recent_tasks,
        'recent_bugs': recent_bugs,
        'pm_tasks_todo': pm_tasks_todo,
        'pm_tasks_inprogress': pm_tasks_inprogress,
        'pm_tasks_completed': pm_tasks_completed,
        'pm_tasks_blocked': pm_tasks_blocked,
    }
    return render(request, 'dashboard/pm_dashboard.html', context)


@dev_required
def developer_dashboard_view(request):
    """Developer Dashboard highlighting personal tasks, bugs, and assigned projects."""
    user = request.user
    try:
        dev_profile = user.employee_profile
        my_projects = dev_profile.assigned_projects.select_related('client', 'project_manager__user').all()
        my_tasks = Task.objects.filter(assigned_developer=dev_profile).select_related('project')
        my_bugs = Bug.objects.filter(assigned_developer=dev_profile).select_related('project')
        my_projects_count = my_projects.count()
        my_tasks_count = my_tasks.count()
        tasks_todo_count = my_tasks.filter(status=Task.Status.TODO).count()
        tasks_inprogress_count = my_tasks.filter(status=Task.Status.IN_PROGRESS).count()
        tasks_completed_count = my_tasks.filter(status=Task.Status.COMPLETED).count()
        tasks_blocked_count = my_tasks.filter(status=Task.Status.BLOCKED).count()
        my_bugs_count = my_bugs.filter(status__in=[Bug.Status.OPEN, Bug.Status.IN_PROGRESS]).count()
        sprint_tasks = my_tasks.exclude(status=Task.Status.COMPLETED).order_by('deadline')[:8]
        assigned_bugs = my_bugs.filter(status__in=[Bug.Status.OPEN, Bug.Status.IN_PROGRESS]).order_by('-reported_date')[:5]
    except Exception:
        my_projects = []
        my_projects_count = 0
        my_tasks_count = 0
        tasks_todo_count = 0
        tasks_inprogress_count = 0
        tasks_completed_count = 0
        tasks_blocked_count = 0
        my_bugs_count = 0
        sprint_tasks = []
        assigned_bugs = []
        my_projects_count = 0
        my_tasks_count = 0
        tasks_todo_count = 0
        tasks_inprogress_count = 0
        tasks_completed_count = 0
        tasks_blocked_count = 0
        my_bugs_count = 0
        sprint_tasks = []
        assigned_bugs = []

    context = {
        'page_title': 'Developer Workspace Dashboard',
        'my_projects': my_projects,
        'my_projects_count': my_projects_count,
        'my_tasks_count': my_tasks_count,
        'tasks_todo_count': tasks_todo_count,
        'tasks_inprogress_count': tasks_inprogress_count,
        'tasks_completed_count': tasks_completed_count,
        'tasks_blocked_count': tasks_blocked_count,
        'my_bugs_count': my_bugs_count,
        'sprint_tasks': sprint_tasks,
        'assigned_bugs': assigned_bugs,
    }
    return render(request, 'dashboard/developer_dashboard.html', context)

import csv
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.decorators import admin_required, hr_required, pm_required, admin_or_pm_required
from accounts.models import User
from employees.models import EmployeeProfile, Department, LeaveRequest
from projects.models import Project
from tasks.models import Task, Bug
from clients.models import Client, Lead


@login_required
def reports_hub_view(request):
    """
    Centralized Intelligence & Analytics Reports Hub.
    Allows Admins, HRs, and PMs to view dataset summaries and trigger CSV exports.
    """
    user = request.user
    if user.is_dev_role:
        messages.error(request, "Access to the Executive Reports Hub is restricted to Management roles.")
        return redirect('dashboard:developer')

    # Aggregated Summary Counts
    total_employees = EmployeeProfile.objects.count()
    total_projects = Project.objects.count()
    total_tasks = Task.objects.count()
    total_leaves = LeaveRequest.objects.count()

    # Previews of latest records (top 5 each)
    latest_employees = EmployeeProfile.objects.select_related('user', 'department').order_by('-joining_date')[:5]
    latest_projects = Project.objects.select_related('client', 'project_manager__user').order_by('-created_at')[:5]
    latest_tasks = Task.objects.select_related('project', 'assigned_developer__user').order_by('-created_at')[:5]
    latest_leaves = LeaveRequest.objects.select_related('employee__user').order_by('-applied_date')[:5]

    context = {
        'page_title': 'Enterprise Intelligence & Reports Hub',
        'total_employees': total_employees,
        'total_projects': total_projects,
        'total_tasks': total_tasks,
        'total_leaves': total_leaves,
        'latest_employees': latest_employees,
        'latest_projects': latest_projects,
        'latest_tasks': latest_tasks,
        'latest_leaves': latest_leaves,
    }
    return render(request, 'dashboard/reports_hub.html', context)


@login_required
def export_employees_csv(request):
    """
    Generates and downloads a CSV export of all employee profiles.
    Permitted Roles: ADMIN, HR
    """
    user = request.user
    if not (user.is_admin_role or user.is_hr_role):
        messages.error(request, "You do not have permission to export employee payroll and record data.")
        return redirect('dashboard:index')

    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f"apex_employees_report_{timestamp}.csv"

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    # Header Row
    writer.writerow([
        'Employee ID',
        'First Name',
        'Last Name',
        'Username',
        'Email',
        'Phone Number',
        'Department',
        'Designation',
        'Employment Status',
        'System Role',
        'Joining Date',
        'Salary (USD)',
        'Active Account'
    ])

    employees = EmployeeProfile.objects.select_related('user', 'department').order_by('employee_id')
    for emp in employees:
        writer.writerow([
            emp.employee_id,
            emp.user.first_name,
            emp.user.last_name,
            emp.user.username,
            emp.email,
            emp.phone_number or 'N/A',
            emp.department.name if emp.department else 'Unassigned',
            emp.designation,
            emp.get_employment_status_display(),
            emp.user.get_role_display(),
            emp.joining_date.strftime('%Y-%m-%d') if emp.joining_date else 'N/A',
            f"{emp.salary:.2f}" if emp.salary else '0.00',
            'Yes' if emp.user.is_active else 'No'
        ])

    return response


@login_required
def export_projects_csv(request):
    """
    Generates and downloads a CSV export of all project delivery records.
    Permitted Roles: ADMIN, HR, PROJECT_MANAGER
    """
    user = request.user
    if not (user.is_admin_role or user.is_hr_role or user.is_pm_role):
        messages.error(request, "You do not have permission to export project portfolio records.")
        return redirect('dashboard:index')

    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f"apex_projects_report_{timestamp}.csv"

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([
        'Project ID',
        'Project Name',
        'Client Organization',
        'Project Manager',
        'Status',
        'Start Date',
        'Deadline',
        'Budget (USD)',
        'Progress (%)',
        'Total Tasks',
        'Completed Tasks',
        'Open Bugs',
        'Overdue Flag'
    ])

    projects = Project.objects.select_related('client', 'project_manager__user').order_by('project_id')
    for p in projects:
        total_t = p.tasks.count()
        completed_t = p.tasks.filter(status=Task.Status.COMPLETED).count()
        open_b = p.bugs.filter(status__in=[Bug.Status.OPEN, Bug.Status.IN_PROGRESS]).count()

        writer.writerow([
            p.project_id,
            p.name,
            p.client.company_name if p.client else 'N/A',
            p.project_manager.full_name if p.project_manager else 'Unassigned',
            p.get_status_display(),
            p.start_date.strftime('%Y-%m-%d') if p.start_date else 'N/A',
            p.deadline.strftime('%Y-%m-%d') if p.deadline else 'N/A',
            f"{p.budget:.2f}" if p.budget else '0.00',
            f"{p.progress_percentage}%",
            total_t,
            completed_t,
            open_b,
            'Yes' if p.is_overdue else 'No'
        ])

    return response


@login_required
def export_tasks_csv(request):
    """
    Generates and downloads a CSV export of sprint backlog tasks.
    Permitted Roles: ADMIN, HR, PROJECT_MANAGER
    """
    user = request.user
    if not (user.is_admin_role or user.is_hr_role or user.is_pm_role):
        messages.error(request, "You do not have permission to export sprint task records.")
        return redirect('dashboard:index')

    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f"apex_tasks_report_{timestamp}.csv"

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([
        'Task ID',
        'Task Title',
        'Project ID',
        'Project Name',
        'Assigned Developer ID',
        'Assigned Developer Name',
        'Priority',
        'Status',
        'Start Date',
        'Deadline',
        'Overdue Flag',
        'Created By'
    ])

    tasks = Task.objects.select_related('project', 'assigned_developer__user', 'created_by').order_by('task_id')
    for t in tasks:
        writer.writerow([
            t.task_id,
            t.title,
            t.project.project_id if t.project else 'N/A',
            t.project.name if t.project else 'N/A',
            t.assigned_developer.employee_id if t.assigned_developer else 'N/A',
            t.assigned_developer.full_name if t.assigned_developer else 'Unassigned',
            t.get_priority_display(),
            t.get_status_display(),
            t.start_date.strftime('%Y-%m-%d') if t.start_date else 'N/A',
            t.deadline.strftime('%Y-%m-%d') if t.deadline else 'N/A',
            'Yes' if t.is_overdue else 'No',
            t.created_by.get_full_name() if (t.created_by and t.created_by.get_full_name()) else (t.created_by.username if t.created_by else 'System')
        ])

    return response


@login_required
def export_leaves_csv(request):
    """
    Generates and downloads a CSV export of employee leave requests.
    Permitted Roles: ADMIN, HR
    """
    user = request.user
    if not (user.is_admin_role or user.is_hr_role):
        messages.error(request, "You do not have permission to export employee leave records.")
        return redirect('dashboard:index')

    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f"apex_leaves_report_{timestamp}.csv"

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([
        'Leave ID',
        'Employee ID',
        'Employee Name',
        'Department',
        'Leave Type',
        'Start Date',
        'End Date',
        'Duration (Days)',
        'Status',
        'Reason',
        'Applied Date',
        'Reviewed By'
    ])

    leaves = LeaveRequest.objects.select_related('employee__user', 'employee__department', 'reviewed_by').order_by('-applied_date')
    for l in leaves:
        writer.writerow([
            f"LV-{l.pk:04d}",
            l.employee.employee_id if l.employee else 'N/A',
            l.employee.full_name if l.employee else 'N/A',
            l.employee.department.name if (l.employee and l.employee.department) else 'Unassigned',
            l.get_leave_type_display(),
            l.start_date.strftime('%Y-%m-%d'),
            l.end_date.strftime('%Y-%m-%d'),
            l.duration_days,
            l.get_status_display(),
            l.reason,
            l.applied_date.strftime('%Y-%m-%d %H:%M'),
            l.reviewed_by.get_full_name() if (l.reviewed_by and l.reviewed_by.get_full_name()) else (l.reviewed_by.username if l.reviewed_by else 'Pending')
        ])

    return response

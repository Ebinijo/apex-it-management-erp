from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from accounts.decorators import admin_required, admin_or_hr_required
from .models import Department, EmployeeProfile, LeaveRequest
from .forms import (
    DepartmentForm,
    EmployeeCreateForm,
    EmployeeUpdateForm,
    LeaveApplicationForm,
    LeaveReviewForm
)

# -------------------------------------------------------------
# EMPLOYEE MANAGEMENT VIEWS
# -------------------------------------------------------------

@login_required
def employee_list_view(request):
    """
    Renders searchable and filterable employee directory table.
    Search by employee name or ID. Filter by department, designation, and status.
    """
    employees = EmployeeProfile.objects.select_related('user', 'department').all().order_by('employee_id')

    # Search by Name or Employee ID
    search_query = request.GET.get('q', '').strip()
    if search_query:
        employees = employees.filter(
            Q(employee_id__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(designation__icontains=search_query) |
            Q(skills__icontains=search_query)
        )

    # Filter by Department
    department_filter = request.GET.get('department', '').strip()
    if department_filter:
        employees = employees.filter(department_id=department_filter)

    # Filter by Designation
    designation_filter = request.GET.get('designation', '').strip()
    if designation_filter:
        employees = employees.filter(designation__icontains=designation_filter)

    # Filter by Employment Status
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        employees = employees.filter(employment_status=status_filter)

    departments = Department.objects.all()
    statuses = EmployeeProfile.EmploymentStatus.choices

    return render(request, 'employees/employee_list.html', {
        'employees': employees,
        'departments': departments,
        'statuses': statuses,
        'search_query': search_query,
        'department_filter': department_filter,
        'designation_filter': designation_filter,
        'status_filter': status_filter,
        'page_title': 'Workforce Directory'
    })


@login_required
def employee_detail_view(request, pk):
    """Displays comprehensive profile for an individual employee."""
    employee = get_object_or_404(EmployeeProfile.objects.select_related('user', 'department'), pk=pk)
    recent_leaves = employee.leave_requests.all().order_by('-applied_at')[:5]

    return render(request, 'employees/employee_detail.html', {
        'employee': employee,
        'recent_leaves': recent_leaves,
        'page_title': f'Employee Profile: {employee.full_name}'
    })


@admin_or_hr_required
def employee_create_view(request):
    """HR / Admin view to add a new employee."""
    if request.method == 'POST':
        form = EmployeeCreateForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f"Employee '{employee.full_name}' ({employee.employee_id}) created successfully.")
            return redirect('employees:detail', pk=employee.pk)
        else:
            messages.error(request, "Please correct the errors in the employee form.")
    else:
        form = EmployeeCreateForm()

    return render(request, 'employees/employee_form.html', {
        'form': form,
        'action': 'Add New',
        'page_title': 'Register New Employee'
    })


@admin_or_hr_required
def employee_edit_view(request, pk):
    """HR / Admin view to edit employee details."""
    employee = get_object_or_404(EmployeeProfile, pk=pk)

    if request.method == 'POST':
        form = EmployeeUpdateForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f"Employee '{employee.full_name}' updated successfully.")
            return redirect('employees:detail', pk=employee.pk)
        else:
            messages.error(request, "Please correct the highlighted errors.")
    else:
        form = EmployeeUpdateForm(instance=employee)

    return render(request, 'employees/employee_form.html', {
        'form': form,
        'action': 'Edit',
        'employee': employee,
        'page_title': f'Edit Employee: {employee.full_name}'
    })


@admin_or_hr_required
def employee_delete_view(request, pk):
    """HR / Admin view to delete an employee record with confirmation."""
    employee = get_object_or_404(EmployeeProfile, pk=pk)

    if request.method == 'POST':
        emp_name = employee.full_name
        # Delete user which cascades to employee profile
        employee.user.delete()
        messages.success(request, f"Employee '{emp_name}' and associated user account have been deleted.")
        return redirect('employees:list')

    return render(request, 'employees/employee_confirm_delete.html', {
        'employee': employee,
        'page_title': f'Confirm Delete: {employee.full_name}'
    })


# -------------------------------------------------------------
# DEPARTMENT MANAGEMENT VIEWS
# -------------------------------------------------------------

@login_required
def department_list_view(request):
    """Lists all company departments with headcount count."""
    departments = Department.objects.annotate(total_members=Count('employees')).all()
    return render(request, 'employees/department_list.html', {
        'departments': departments,
        'page_title': 'Departments Directory'
    })


@admin_or_hr_required
def department_create_view(request):
    """Creates a new company department."""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f"Department '{dept.name}' created successfully.")
            return redirect('employees:department_list')
        else:
            messages.error(request, "Please resolve the form errors.")
    else:
        form = DepartmentForm()

    return render(request, 'employees/department_form.html', {
        'form': form,
        'action': 'Create',
        'page_title': 'Add New Department'
    })


@admin_or_hr_required
def department_edit_view(request, pk):
    """Edits an existing department."""
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, f"Department '{department.name}' updated successfully.")
            return redirect('employees:department_list')
        else:
            messages.error(request, "Please fix the errors.")
    else:
        form = DepartmentForm(instance=department)

    return render(request, 'employees/department_form.html', {
        'form': form,
        'action': 'Edit',
        'department': department,
        'page_title': f'Edit Department: {department.name}'
    })


@admin_or_hr_required
def department_delete_view(request, pk):
    """Deletes department if no active employees are assigned."""
    department = get_object_or_404(Department, pk=pk)
    if department.employees.exists():
        messages.error(
            request,
            f"Cannot delete department '{department.name}' because {department.employees.count()} employees are currently assigned to it."
        )
        return redirect('employees:department_list')

    if request.method == 'POST':
        name = department.name
        department.delete()
        messages.success(request, f"Department '{name}' has been deleted.")
        return redirect('employees:department_list')

    return render(request, 'employees/department_confirm_delete.html', {
        'department': department,
        'page_title': f'Confirm Delete: {department.name}'
    })


# -------------------------------------------------------------
# LEAVE APPLICATION & APPROVAL WORKFLOW VIEWS
# -------------------------------------------------------------

@login_required
def leave_list_view(request):
    """
    Renders leave requests.
    - HR / Admin: View ALL requests with filter by status.
    - Developers / PMs: View their OWN leave requests.
    """
    user = request.user
    status_filter = request.GET.get('status', '').strip()

    if user.is_admin_role or user.is_hr_role:
        leave_requests = LeaveRequest.objects.select_related('employee__user', 'reviewed_by').all()
        is_approver = True
    else:
        if hasattr(user, 'employee_profile'):
            leave_requests = user.employee_profile.leave_requests.select_related('reviewed_by').all()
        else:
            leave_requests = LeaveRequest.objects.none()
        is_approver = False

    if status_filter:
        leave_requests = leave_requests.filter(status=status_filter)

    # Leave status counts for tabs
    if user.is_admin_role or user.is_hr_role:
        total_count = LeaveRequest.objects.count()
        pending_count = LeaveRequest.objects.filter(status=LeaveRequest.Status.PENDING).count()
        approved_count = LeaveRequest.objects.filter(status=LeaveRequest.Status.APPROVED).count()
        rejected_count = LeaveRequest.objects.filter(status=LeaveRequest.Status.REJECTED).count()
    elif hasattr(user, 'employee_profile'):
        emp_leaves = user.employee_profile.leave_requests.all()
        total_count = emp_leaves.count()
        pending_count = emp_leaves.filter(status=LeaveRequest.Status.PENDING).count()
        approved_count = emp_leaves.filter(status=LeaveRequest.Status.APPROVED).count()
        rejected_count = emp_leaves.filter(status=LeaveRequest.Status.REJECTED).count()
    else:
        total_count = pending_count = approved_count = rejected_count = 0

    return render(request, 'employees/leave_list.html', {
        'leave_requests': leave_requests,
        'status_filter': status_filter,
        'is_approver': is_approver,
        'total_count': total_count,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'page_title': 'Leave Management'
    })


@login_required
def leave_apply_view(request):
    """Allows an employee to apply for leave."""
    user = request.user

    # Auto-provision profile for admin/test accounts if missing
    if not hasattr(user, 'employee_profile'):
        dept = Department.objects.first()
        EmployeeProfile.objects.create(
            user=user,
            employee_id=f"EMP-{user.id:03d}",
            department=dept,
            designation=user.designation or user.get_role_display(),
            phone=user.phone or ''
        )

    employee = user.employee_profile

    if request.method == 'POST':
        form = LeaveApplicationForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = employee
            leave.status = LeaveRequest.Status.PENDING
            leave.save()
            messages.success(request, f"Your leave application ({leave.duration_days} day(s)) has been submitted for HR approval.")
            return redirect('employees:leave_list')
        else:
            messages.error(request, "Please correct the errors in the leave application.")
    else:
        form = LeaveApplicationForm()

    return render(request, 'employees/leave_apply.html', {
        'form': form,
        'employee': employee,
        'page_title': 'Apply for Leave'
    })


@admin_or_hr_required
def leave_action_view(request, pk):
    """
    HR / Admin review view to Approve or Reject a leave application.
    Enforces validation: an employee CANNOT approve their own leave request.
    """
    leave_req = get_object_or_404(LeaveRequest.objects.select_related('employee__user'), pk=pk)

    # Self-approval restriction
    if leave_req.employee.user == request.user:
        messages.error(request, "Access Denied: You cannot approve or reject your own leave request.")
        return redirect('employees:leave_list')

    if request.method == 'POST':
        action = request.POST.get('action')
        remarks = request.POST.get('admin_remarks', '').strip()

        if action == 'APPROVE':
            leave_req.status = LeaveRequest.Status.APPROVED
            leave_req.reviewed_by = request.user
            leave_req.reviewed_at = timezone.now()
            leave_req.admin_remarks = remarks
            leave_req.save()
            messages.success(request, f"Leave application for '{leave_req.employee.full_name}' was APPROVED.")
        elif action == 'REJECT':
            leave_req.status = LeaveRequest.Status.REJECTED
            leave_req.reviewed_by = request.user
            leave_req.reviewed_at = timezone.now()
            leave_req.admin_remarks = remarks
            leave_req.save()
            messages.warning(request, f"Leave application for '{leave_req.employee.full_name}' was REJECTED.")
        else:
            messages.error(request, "Invalid action selected.")

        return redirect('employees:leave_list')

    return render(request, 'employees/leave_review.html', {
        'leave_req': leave_req,
        'page_title': f'Review Leave Request: {leave_req.employee.full_name}'
    })

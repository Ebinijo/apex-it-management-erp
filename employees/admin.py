from django.contrib import admin
from .models import Department, EmployeeProfile, LeaveRequest

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'employee_count', 'created_at')
    search_fields = ('name', 'code')


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'department', 'designation', 'employment_status', 'joining_date')
    list_filter = ('department', 'employment_status', 'gender', 'joining_date')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'user__username', 'user__email', 'designation')


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'duration_days', 'status', 'reviewed_by')
    list_filter = ('status', 'leave_type', 'applied_at')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'employee__employee_id', 'reason')

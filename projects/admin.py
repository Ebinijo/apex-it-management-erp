from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_id', 'name', 'client', 'project_manager', 'status', 'start_date', 'deadline', 'progress_percentage')
    list_filter = ('status', 'start_date', 'deadline', 'client')
    search_fields = ('project_id', 'name', 'client__company_name', 'project_manager__user__first_name', 'project_manager__user__last_name')
    filter_horizontal = ('team_members',)

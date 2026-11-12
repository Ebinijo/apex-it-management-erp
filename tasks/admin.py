from django.contrib import admin
from .models import Task, Bug

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'title', 'project', 'assigned_developer', 'priority', 'status', 'deadline', 'is_overdue')
    list_filter = ('status', 'priority', 'project', 'deadline')
    search_fields = ('task_id', 'title', 'project__name', 'assigned_developer__user__first_name', 'assigned_developer__user__last_name')


@admin.register(Bug)
class BugAdmin(admin.ModelAdmin):
    list_display = ('bug_id', 'title', 'project', 'priority', 'status', 'assigned_developer', 'reported_by', 'reported_date')
    list_filter = ('status', 'priority', 'project', 'reported_date')
    search_fields = ('bug_id', 'title', 'project__name', 'description')

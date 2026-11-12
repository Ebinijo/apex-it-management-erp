from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from projects.models import Project
from employees.models import EmployeeProfile

class Task(models.Model):
    """
    Individual engineering work unit assigned to a developer under a project.
    """
    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low Priority'
        MEDIUM = 'MEDIUM', 'Medium Priority'
        HIGH = 'HIGH', 'High Priority'
        CRITICAL = 'CRITICAL', 'Critical / Urgent'

    class Status(models.TextChoices):
        TODO = 'TODO', 'To Do'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        BLOCKED = 'BLOCKED', 'Blocked'

    task_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique Task Identifier (e.g. TSK-001)"
    )
    title = models.CharField(max_length=150, help_text="Actionable task title")
    description = models.TextField(blank=True, help_text="Technical acceptance criteria and implementation details")
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text="Associated software project"
    )
    assigned_developer = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        help_text="Assigned developer executing this work unit"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tasks',
        help_text="Project Manager or Admin who created the task"
    )
    
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    
    start_date = models.DateField(default=timezone.now, help_text="Task start date")
    deadline = models.DateField(help_text="Target task completion deadline")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['deadline', '-priority']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def clean(self):
        super().clean()
        if self.start_date and self.deadline:
            if self.deadline < self.start_date:
                raise ValidationError({
                    'deadline': "Task deadline cannot be earlier than start date."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.task_id} - {self.title} [{self.get_status_display()}]"

    @property
    def is_overdue(self):
        """Highlights overdue tasks if deadline has passed and task is not completed."""
        if self.deadline and self.status != self.Status.COMPLETED:
            return timezone.now().date() > self.deadline
        return False

    @property
    def status_badge_class(self):
        badges = {
            self.Status.TODO: 'bg-secondary',
            self.Status.IN_PROGRESS: 'bg-primary',
            self.Status.COMPLETED: 'bg-success',
            self.Status.BLOCKED: 'bg-danger',
        }
        return badges.get(self.status, 'bg-secondary')

    @property
    def priority_badge_class(self):
        badges = {
            self.Priority.LOW: 'bg-light text-secondary border',
            self.Priority.MEDIUM: 'bg-info text-dark',
            self.Priority.HIGH: 'bg-warning text-dark',
            self.Priority.CRITICAL: 'bg-danger text-white',
        }
        return badges.get(self.priority, 'bg-secondary')


class Bug(models.Model):
    """
    Defect or issue report linked to a project and assigned for engineering resolution.
    """
    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low Severity'
        MEDIUM = 'MEDIUM', 'Medium Severity'
        HIGH = 'HIGH', 'High Severity'
        CRITICAL = 'CRITICAL', 'Critical Blocker'

    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'

    bug_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique Bug Identifier (e.g. BUG-001)"
    )
    title = models.CharField(max_length=150, help_text="Summary of defect or abnormal behavior")
    description = models.TextField(help_text="Steps to reproduce, expected vs actual behavior, stack traces")
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='bugs',
        help_text="Project in which defect was discovered"
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reported_bugs',
        help_text="User/Developer who discovered and logged the issue"
    )
    assigned_developer = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_bugs',
        help_text="Developer tasked with investigating and fixing defect"
    )
    
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.HIGH)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    reported_date = models.DateField(default=timezone.now)
    resolution_notes = models.TextField(blank=True, help_text="Root cause diagnosis, commit reference, or patch notes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Bug Issue'
        verbose_name_plural = 'Bug Issues'

    def __str__(self):
        return f"{self.bug_id} - {self.title} ({self.project.name}) [{self.get_status_display()}]"

    @property
    def status_badge_class(self):
        badges = {
            self.Status.OPEN: 'bg-danger',
            self.Status.IN_PROGRESS: 'bg-warning text-dark',
            self.Status.RESOLVED: 'bg-success',
            self.Status.CLOSED: 'bg-secondary',
        }
        return badges.get(self.status, 'bg-secondary')

    @property
    def priority_badge_class(self):
        badges = {
            self.Priority.LOW: 'bg-light text-secondary border',
            self.Priority.MEDIUM: 'bg-info text-dark',
            self.Priority.HIGH: 'bg-warning text-dark',
            self.Priority.CRITICAL: 'bg-danger text-white',
        }
        return badges.get(self.priority, 'bg-secondary')

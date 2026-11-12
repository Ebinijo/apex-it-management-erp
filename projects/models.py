from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from clients.models import Client
from employees.models import EmployeeProfile

class Project(models.Model):
    """
    Client software project tracked across engineering lifecycles.
    """
    class Status(models.TextChoices):
        PLANNING = 'PLANNING', 'Planning & Scoping'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        TESTING = 'TESTING', 'Testing & QA'
        COMPLETED = 'COMPLETED', 'Completed'
        ON_HOLD = 'ON_HOLD', 'On Hold'

    project_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique Project Identifier (e.g. PRJ-001)"
    )
    name = models.CharField(max_length=150, help_text="Official Project Title")
    description = models.TextField(blank=True, help_text="Detailed project requirements, architecture and deliverables")
    
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='projects',
        help_text="Contracted corporate client"
    )
    project_manager = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_projects',
        help_text="Assigned Project Manager overseeing delivery"
    )
    team_members = models.ManyToManyField(
        EmployeeProfile,
        related_name='assigned_projects',
        blank=True,
        help_text="Engineering team developers allocated to project"
    )
    
    start_date = models.DateField(default=timezone.now, help_text="Sprint start date")
    deadline = models.DateField(help_text="Target delivery deadline")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNING)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def clean(self):
        super().clean()
        if self.start_date and self.deadline:
            if self.deadline < self.start_date:
                raise ValidationError({
                    'deadline': "Project deadline cannot be earlier than start date."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project_id} - {self.name} ({self.client.company_name})"

    @property
    def total_tasks_count(self):
        """Returns total tasks created under this project (Phase 5)."""
        if hasattr(self, 'tasks'):
            return self.tasks.count()
        return 0

    @property
    def completed_tasks_count(self):
        """Returns count of completed tasks under this project."""
        if hasattr(self, 'tasks'):
            return self.tasks.filter(status='COMPLETED').count()
        return 0

    @property
    def pending_tasks_count(self):
        """Returns count of pending tasks under this project."""
        if hasattr(self, 'tasks'):
            return self.tasks.exclude(status='COMPLETED').count()
        return 0

    @property
    def open_bugs_count(self):
        """Returns count of open / in-progress reported bugs."""
        if hasattr(self, 'bugs'):
            return self.bugs.exclude(status__in=['RESOLVED', 'CLOSED']).count()
        return 0

    @property
    def progress_percentage(self):
        """
        Calculates project progress: (completed_tasks / total_tasks) * 100.
        Returns 0 if no tasks exist, strictly from actual database records.
        """
        if hasattr(self, 'tasks'):
            total = self.tasks.count()
            if total > 0:
                completed = self.tasks.filter(status='COMPLETED').count()
                return int((completed / total) * 100)
        return 0

    @property
    def is_overdue(self):
        """Checks if current date is past deadline and project is not completed."""
        if self.deadline and self.status != self.Status.COMPLETED:
            return timezone.now().date() > self.deadline
        return False

    @property
    def status_badge_class(self):
        badges = {
            self.Status.PLANNING: 'bg-info text-dark',
            self.Status.IN_PROGRESS: 'bg-primary',
            self.Status.TESTING: 'bg-warning text-dark',
            self.Status.COMPLETED: 'bg-success',
            self.Status.ON_HOLD: 'bg-secondary',
        }
        return badges.get(self.status, 'bg-secondary')

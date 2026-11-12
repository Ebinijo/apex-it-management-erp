from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

class Department(models.Model):
    """
    Department within the IT organization (e.g. Engineering, QA, HR).
    """
    name = models.CharField(max_length=100, unique=True, help_text="Department name")
    code = models.CharField(max_length=20, unique=True, help_text="Unique short code (e.g. ENG, QA, HR)")
    description = models.TextField(blank=True, help_text="Department responsibilities and scope")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def employee_count(self):
        return self.employees.count()


class EmployeeProfile(models.Model):
    """
    Detailed employee record linked One-to-One with the User authentication model.
    """
    class Gender(models.TextChoices):
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'
        OTHER = 'OTHER', 'Other'
        PREFER_NOT_TO_SAY = 'PREFER_NOT_TO_SAY', 'Prefer not to say'

    class EmploymentStatus(models.TextChoices):
        FULL_TIME = 'FULL_TIME', 'Full-Time'
        PART_TIME = 'PART_TIME', 'Part-Time'
        CONTRACT = 'CONTRACT', 'Contractor'
        INTERN = 'INTERN', 'Intern'
        RESIGNED = 'RESIGNED', 'Resigned'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        help_text="Associated system user credentials"
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique Employee Identification Code (e.g. EMP-001)"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        help_text="Assigned company department"
    )
    designation = models.CharField(max_length=100, help_text="Official job title")
    gender = models.CharField(max_length=20, choices=Gender.choices, default=Gender.PREFER_NOT_TO_SAY)
    phone = models.CharField(max_length=20, blank=True, help_text="Contact number")
    joining_date = models.DateField(default=timezone.now, help_text="Date joined the organization")
    skills = models.TextField(
        blank=True,
        help_text="Comma-separated technical competencies (e.g. Python, Django, Docker, AWS)"
    )
    employment_status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.FULL_TIME
    )
    emergency_contact = models.CharField(max_length=100, blank=True, help_text="Emergency contact person and phone")
    address = models.TextField(blank=True, help_text="Residential postal address")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['employee_id']
        verbose_name = 'Employee Profile'
        verbose_name_plural = 'Employee Profiles'

    def __str__(self):
        return f"{self.employee_id} - {self.full_name} ({self.designation})"

    @property
    def full_name(self):
        full = self.user.get_full_name()
        return full if full else self.user.username

    @property
    def email(self):
        return self.user.email

    @property
    def skills_list(self):
        """Returns clean list of skills for rendering as chips/tags."""
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    @property
    def status_badge_class(self):
        badges = {
            self.EmploymentStatus.FULL_TIME: 'bg-success',
            self.EmploymentStatus.PART_TIME: 'bg-info text-dark',
            self.EmploymentStatus.CONTRACT: 'bg-warning text-dark',
            self.EmploymentStatus.INTERN: 'bg-primary',
            self.EmploymentStatus.RESIGNED: 'bg-secondary',
        }
        return badges.get(self.employment_status, 'bg-secondary')


class LeaveRequest(models.Model):
    """
    Leave application submitted by an employee with approval workflow.
    """
    class LeaveType(models.TextChoices):
        CASUAL = 'CASUAL', 'Casual Leave'
        SICK = 'SICK', 'Sick / Medical Leave'
        ANNUAL = 'ANNUAL', 'Annual Paid Leave'
        MATERNITY_PATERNITY = 'MATERNITY_PATERNITY', 'Maternity / Paternity Leave'
        UNPAID = 'UNPAID', 'Leave Without Pay'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name='leave_requests',
        help_text="Employee applying for leave"
    )
    leave_type = models.CharField(max_length=30, choices=LeaveType.choices, default=LeaveType.CASUAL)
    start_date = models.DateField(help_text="First day of leave")
    end_date = models.DateField(help_text="Last day of leave")
    reason = models.TextField(help_text="Detailed justification for leave")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_leaves',
        help_text="HR or Admin who approved/rejected the request"
    )
    admin_remarks = models.TextField(blank=True, help_text="Feedback or remarks from HR/Admin")
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-applied_at']
        verbose_name = 'Leave Request'
        verbose_name_plural = 'Leave Requests'

    def clean(self):
        """Backend model validation for date logic and self-approval."""
        super().clean()
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError({
                    'end_date': "Leave end date cannot be earlier than start date."
                })

        # Self-approval check: Employee cannot approve their own leave request
        if self.reviewed_by and self.employee and self.reviewed_by == self.employee.user:
            raise ValidationError({
                'reviewed_by': "Employees are strictly prohibited from approving their own leave applications."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def duration_days(self):
        """Calculates total leave duration in calendar days (inclusive)."""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    @property
    def status_badge_class(self):
        badges = {
            self.Status.PENDING: 'bg-warning text-dark',
            self.Status.APPROVED: 'bg-success',
            self.Status.REJECTED: 'bg-danger',
        }
        return badges.get(self.status, 'bg-secondary')

    def __str__(self):
        return f"{self.employee.full_name} ({self.get_leave_type_display()}): {self.start_date} to {self.end_date} [{self.get_status_display()}]"

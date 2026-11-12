from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Includes role-based access control (ADMIN, HR, PROJECT_MANAGER, DEVELOPER).
    """
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        HR = 'HR', 'HR Manager'
        PROJECT_MANAGER = 'PROJECT_MANAGER', 'Project Manager'
        DEVELOPER = 'DEVELOPER', 'Developer'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.DEVELOPER,
        help_text='Designates the role and permission tier of the user.'
    )
    phone = models.CharField(max_length=20, blank=True, null=True, help_text='Contact phone number')
    designation = models.CharField(max_length=100, blank=True, null=True, help_text='Official job designation')
    profile_picture = models.ImageField(upload_to='avatars/', blank=True, null=True, help_text='Profile display photo')
    bio = models.TextField(blank=True, null=True, help_text='Brief professional summary')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def role_badge_class(self):
        """Returns Bootstrap badge color class based on role."""
        badges = {
            self.Role.ADMIN: 'bg-danger',
            self.Role.HR: 'bg-warning text-dark',
            self.Role.PROJECT_MANAGER: 'bg-info text-dark',
            self.Role.DEVELOPER: 'bg-primary',
        }
        return badges.get(self.role, 'bg-secondary')

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_hr_role(self):
        return self.role == self.Role.HR or self.is_superuser

    @property
    def is_pm_role(self):
        return self.role == self.Role.PROJECT_MANAGER or self.is_superuser

    @property
    def is_dev_role(self):
        return self.role == self.Role.DEVELOPER

    def __str__(self):
        full = self.get_full_name()
        return f"{full} ({self.get_role_display()})" if full else f"{self.username} ({self.get_role_display()})"

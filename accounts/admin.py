from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for Custom User model."""
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'designation', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'designation', 'phone')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Company Role & Profile Details', {
            'fields': ('role', 'designation', 'phone', 'profile_picture', 'bio')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Company Role & Profile Details', {
            'fields': ('role', 'designation', 'phone', 'email', 'first_name', 'last_name')
        }),
    )

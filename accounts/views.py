from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import User
from .forms import (
    LoginForm,
    UserProfileUpdateForm,
    CustomPasswordChangeForm,
    AdminUserCreateForm,
    AdminUserUpdateForm
)
from .decorators import admin_required

def login_view(request):
    """Handles user authentication and redirection."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.error(request, "Your account is deactivated. Please contact the administrator.")
                return redirect('accounts:login')
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect('dashboard:index')
        else:
            messages.error(request, "Invalid username or password. Please verify your credentials.")
    else:
        form = LoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Logs out the user and clears session."""
    user_name = request.user.get_full_name() or request.user.username
    logout(request)
    messages.info(request, f"Goodbye {user_name}, you have been safely logged out.")
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """View and update profile information for the logged-in user."""
    user = request.user
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been successfully updated.")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the errors in the profile form.")
    else:
        form = UserProfileUpdateForm(instance=user)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'user': user,
        'page_title': 'My Profile'
    })


@login_required
def change_password_view(request):
    """Allows authenticated users to change their account password."""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Keeps the user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'accounts/change_password.html', {
        'form': form,
        'page_title': 'Change Password'
    })


# -------------------------------------------------------------
# Admin User Management Views
# -------------------------------------------------------------

@admin_required
def user_list_view(request):
    """Admin-only view to inspect, search, and manage user accounts."""
    users = User.objects.all().order_by('-date_joined')

    # Search functionality
    search_query = request.GET.get('q', '').strip()
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(designation__icontains=search_query)
        )

    # Filter by role
    role_filter = request.GET.get('role', '').strip()
    if role_filter:
        users = users.filter(role=role_filter)

    # Filter by active status
    status_filter = request.GET.get('status', '').strip()
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)

    return render(request, 'accounts/user_list.html', {
        'users': users,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'roles': User.Role.choices,
        'page_title': 'User Management'
    })


@admin_required
def user_create_view(request):
    """Admin creates a new user account with assigned role."""
    if request.method == 'POST':
        form = AdminUserCreateForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            messages.success(request, f"User account '{new_user.username}' created successfully!")
            return redirect('accounts:user_list')
        else:
            messages.error(request, "Please check the form inputs.")
    else:
        form = AdminUserCreateForm()

    return render(request, 'accounts/user_form.html', {
        'form': form,
        'action': 'Create',
        'page_title': 'Create New User'
    })


@admin_required
def user_edit_view(request, pk):
    """Admin edits an existing user's details and role."""
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = AdminUserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"User '{user_obj.username}' updated successfully.")
            return redirect('accounts:user_list')
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = AdminUserUpdateForm(instance=user_obj)

    return render(request, 'accounts/user_form.html', {
        'form': form,
        'action': 'Edit',
        'user_obj': user_obj,
        'page_title': f'Edit User: {user_obj.username}'
    })


@admin_required
def user_toggle_status_view(request, pk):
    """Admin toggles user account active / deactivated state."""
    user_obj = get_object_or_404(User, pk=pk)
    if user_obj == request.user:
        messages.warning(request, "You cannot deactivate your own administrative account.")
        return redirect('accounts:user_list')

    user_obj.is_active = not user_obj.is_active
    user_obj.save()
    status_str = "activated" if user_obj.is_active else "deactivated"
    messages.success(request, f"Account for '{user_obj.username}' has been {status_str}.")
    return redirect('accounts:user_list')


# Custom HTTP Error Handlers
def error_403_view(request, exception=None):
    return render(request, 'errors/403.html', status=403)

def error_404_view(request, exception=None):
    return render(request, 'errors/404.html', status=404)

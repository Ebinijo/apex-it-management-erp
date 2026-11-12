from functools import wraps
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles):
    """
    Decorator for views that checks whether the logged-in user
    has one of the allowed roles. Superusers always have full access.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access this page.")
                return redirect(f"/accounts/login/?next={request.path}")

            if not request.user.is_active:
                messages.error(request, "Your account has been deactivated. Please contact an administrator.")
                return redirect('accounts:login')

            # Superuser bypasses all role restrictions
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            # Access denied for authenticated user lacking required role
            return render(request, 'errors/403.html', {
                'required_roles': allowed_roles,
                'user_role': request.user.get_role_display(),
            }, status=403)

        return _wrapped_view
    return decorator


# Convenience decorators for role checking
def admin_required(view_func):
    return role_required(['ADMIN'])(view_func)

def hr_required(view_func):
    return role_required(['HR', 'ADMIN'])(view_func)

def pm_required(view_func):
    return role_required(['PROJECT_MANAGER', 'ADMIN'])(view_func)

def dev_required(view_func):
    return role_required(['DEVELOPER', 'ADMIN'])(view_func)

def admin_or_hr_required(view_func):
    return role_required(['ADMIN', 'HR'])(view_func)

def admin_or_pm_required(view_func):
    return role_required(['ADMIN', 'PROJECT_MANAGER'])(view_func)

def admin_hr_pm_required(view_func):
    return role_required(['ADMIN', 'HR', 'PROJECT_MANAGER'])(view_func)

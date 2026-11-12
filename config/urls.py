"""
URL configuration for IT Company Management System.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.http import HttpResponse

def root_redirect(request):
    """Clean root redirect: authenticated users to dashboard, visitors to login."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    return redirect('accounts:login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_redirect, name='root'),
    path('favicon.ico', lambda request: HttpResponse(status=204)),  # Avoid 404 console noise
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('employees/', include('employees.urls', namespace='employees')),
    path('clients/', include('clients.urls', namespace='clients')),
    path('projects/', include('projects.urls', namespace='projects')),
    path('tasks/', include('tasks.urls', namespace='tasks')),
]

# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# Handler for HTTP 403 Forbidden
handler403 = 'accounts.views.error_403_view'
handler404 = 'accounts.views.error_404_view'


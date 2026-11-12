from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Task Management
    path('', views.task_list_view, name='list'),
    path('create/', views.task_create_view, name='create'),
    path('<int:pk>/', views.task_detail_view, name='detail'),
    path('<int:pk>/edit/', views.task_edit_view, name='edit'),
    path('<int:pk>/delete/', views.task_delete_view, name='delete'),
    path('<int:pk>/status-update/', views.task_status_update_view, name='status_update'),

    # Bug Tracking
    path('bugs/', views.bug_list_view, name='bug_list'),
    path('bugs/report/', views.bug_report_view, name='bug_report'),
    path('bugs/<int:pk>/', views.bug_detail_view, name='bug_detail'),
    path('bugs/<int:pk>/edit/', views.bug_edit_view, name='bug_edit'),
    path('bugs/<int:pk>/delete/', views.bug_delete_view, name='bug_delete'),
]

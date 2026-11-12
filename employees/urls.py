from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    # Employee Directory & CRUD
    path('', views.employee_list_view, name='list'),
    path('create/', views.employee_create_view, name='create'),
    path('<int:pk>/', views.employee_detail_view, name='detail'),
    path('<int:pk>/edit/', views.employee_edit_view, name='edit'),
    path('<int:pk>/delete/', views.employee_delete_view, name='delete'),

    # Department Management
    path('departments/', views.department_list_view, name='department_list'),
    path('departments/create/', views.department_create_view, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit_view, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete_view, name='department_delete'),

    # Leave Management Workflow
    path('leaves/', views.leave_list_view, name='leave_list'),
    path('leaves/apply/', views.leave_apply_view, name='leave_apply'),
    path('leaves/<int:pk>/review/', views.leave_action_view, name='leave_review'),
]

from django.urls import path
from . import views
from . import reports

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('admin-panel/', views.admin_dashboard_view, name='admin'),
    path('hr-panel/', views.hr_dashboard_view, name='hr'),
    path('pm-panel/', views.pm_dashboard_view, name='pm'),
    path('dev-panel/', views.developer_dashboard_view, name='developer'),

    # Reports Hub & CSV Exports
    path('reports/', reports.reports_hub_view, name='reports'),
    path('reports/employees/export/', reports.export_employees_csv, name='export_employees'),
    path('reports/projects/export/', reports.export_projects_csv, name='export_projects'),
    path('reports/tasks/export/', reports.export_tasks_csv, name='export_tasks'),
    path('reports/leaves/export/', reports.export_leaves_csv, name='export_leaves'),
]

from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    # Client Management
    path('', views.client_list_view, name='list'),
    path('create/', views.client_create_view, name='create'),
    path('<int:pk>/', views.client_detail_view, name='detail'),
    path('<int:pk>/edit/', views.client_edit_view, name='edit'),
    path('<int:pk>/delete/', views.client_delete_view, name='delete'),

    # Lead Management Pipeline
    path('leads/', views.lead_list_view, name='lead_list'),
    path('leads/create/', views.lead_create_view, name='lead_create'),
    path('leads/<int:pk>/', views.lead_detail_view, name='lead_detail'),
    path('leads/<int:pk>/edit/', views.lead_edit_view, name='lead_edit'),
    path('leads/<int:pk>/delete/', views.lead_delete_view, name='lead_delete'),
    path('leads/<int:pk>/convert/', views.lead_convert_view, name='lead_convert'),
]

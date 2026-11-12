from django.contrib import admin
from .models import Client, Lead

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'company_name', 'contact_person', 'email', 'phone', 'industry', 'registration_date')
    list_filter = ('industry', 'registration_date')
    search_fields = ('client_id', 'company_name', 'contact_person', 'email', 'phone')


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('lead_id', 'title', 'organization_name', 'contact_person', 'status', 'lead_source', 'assigned_employee', 'created_at')
    list_filter = ('status', 'lead_source', 'created_at')
    search_fields = ('lead_id', 'title', 'organization_name', 'contact_person', 'email')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from accounts.decorators import admin_required, admin_hr_pm_required
from .models import Client, Lead
from .forms import ClientForm, LeadForm, LeadConvertForm

# -------------------------------------------------------------
# CLIENT MANAGEMENT VIEWS
# -------------------------------------------------------------

@login_required
@admin_hr_pm_required
def client_list_view(request):
    """
    Searchable and filterable clients directory.
    Search by company name, contact person, or Client ID. Filter by industry.
    """
    clients = Client.objects.all().order_by('company_name')

    # Search
    search_query = request.GET.get('q', '').strip()
    if search_query:
        clients = clients.filter(
            Q(company_name__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(client_id__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Filter by Industry
    industry_filter = request.GET.get('industry', '').strip()
    if industry_filter:
        clients = clients.filter(industry=industry_filter)

    industries = Client.Industry.choices

    return render(request, 'clients/client_list.html', {
        'clients': clients,
        'industries': industries,
        'search_query': search_query,
        'industry_filter': industry_filter,
        'page_title': 'Corporate Clients Directory'
    })


@login_required
@admin_hr_pm_required
def client_detail_view(request, pk):
    """Detailed profile view for an individual corporate client."""
    client = get_object_or_404(Client, pk=pk)
    converted_leads = client.converted_from_leads.all()

    return render(request, 'clients/client_detail.html', {
        'client': client,
        'converted_leads': converted_leads,
        'page_title': f'Client: {client.company_name}'
    })


@login_required
@admin_hr_pm_required
def client_create_view(request):
    """Registers a new corporate client."""
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, f"Client '{client.company_name}' ({client.client_id}) onboarded successfully.")
            return redirect('clients:detail', pk=client.pk)
        else:
            messages.error(request, "Please correct the errors in the client form.")
    else:
        form = ClientForm()

    return render(request, 'clients/client_form.html', {
        'form': form,
        'action': 'Onboard New',
        'page_title': 'Register New Client'
    })


@login_required
@admin_hr_pm_required
def client_edit_view(request, pk):
    """Updates existing client details."""
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, f"Client '{client.company_name}' updated successfully.")
            return redirect('clients:detail', pk=client.pk)
        else:
            messages.error(request, "Please correct the highlighted form errors.")
    else:
        form = ClientForm(instance=client)

    return render(request, 'clients/client_form.html', {
        'form': form,
        'action': 'Edit',
        'client': client,
        'page_title': f'Edit Client: {client.company_name}'
    })


@login_required
@admin_hr_pm_required
def client_delete_view(request, pk):
    """Deletes client record with confirmation."""
    client = get_object_or_404(Client, pk=pk)

    if request.method == 'POST':
        name = client.company_name
        client.delete()
        messages.success(request, f"Client '{name}' has been deleted.")
        return redirect('clients:list')

    return render(request, 'clients/client_confirm_delete.html', {
        'client': client,
        'page_title': f'Confirm Delete: {client.company_name}'
    })


# -------------------------------------------------------------
# LEAD MANAGEMENT VIEWS
# -------------------------------------------------------------

@login_required
@admin_hr_pm_required
def lead_list_view(request):
    """
    Searchable and filterable sales opportunity leads pipeline.
    Search by title, organization name, or contact person. Filter by status.
    """
    leads = Lead.objects.select_related('assigned_employee__user', 'converted_client').all()

    # Search
    search_query = request.GET.get('q', '').strip()
    if search_query:
        leads = leads.filter(
            Q(title__icontains=search_query) |
            Q(organization_name__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(lead_id__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Filter by Status
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        leads = leads.filter(status=status_filter)

    # Pipeline Status Counts
    total_leads = Lead.objects.count()
    new_count = Lead.objects.filter(status=Lead.Status.NEW).count()
    contacted_count = Lead.objects.filter(status=Lead.Status.CONTACTED).count()
    converted_count = Lead.objects.filter(status=Lead.Status.CONVERTED).count()
    lost_count = Lead.objects.filter(status=Lead.Status.LOST).count()

    return render(request, 'clients/lead_list.html', {
        'leads': leads,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_leads': total_leads,
        'new_count': new_count,
        'contacted_count': contacted_count,
        'converted_count': converted_count,
        'lost_count': lost_count,
        'statuses': Lead.Status.choices,
        'page_title': 'Sales Leads Pipeline'
    })


@login_required
@admin_hr_pm_required
def lead_detail_view(request, pk):
    """Comprehensive details of an individual sales opportunity lead."""
    lead = get_object_or_404(Lead.objects.select_related('assigned_employee__user', 'converted_client'), pk=pk)

    return render(request, 'clients/lead_detail.html', {
        'lead': lead,
        'page_title': f'Lead: {lead.title}'
    })


@login_required
@admin_hr_pm_required
def lead_create_view(request):
    """Registers a new sales lead."""
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save()
            messages.success(request, f"Lead '{lead.title}' ({lead.lead_id}) recorded successfully.")
            return redirect('clients:lead_detail', pk=lead.pk)
        else:
            messages.error(request, "Please fix the errors in the lead form.")
    else:
        form = LeadForm()

    return render(request, 'clients/lead_form.html', {
        'form': form,
        'action': 'Create',
        'page_title': 'Record New Sales Opportunity'
    })


@login_required
@admin_hr_pm_required
def lead_edit_view(request, pk):
    """Updates lead information, status or assigned personnel."""
    lead = get_object_or_404(Lead, pk=pk)

    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, f"Lead '{lead.title}' updated successfully.")
            return redirect('clients:lead_detail', pk=lead.pk)
        else:
            messages.error(request, "Please resolve the form errors.")
    else:
        form = LeadForm(instance=lead)

    return render(request, 'clients/lead_form.html', {
        'form': form,
        'action': 'Edit',
        'lead': lead,
        'page_title': f'Edit Lead: {lead.title}'
    })


@login_required
@admin_hr_pm_required
def lead_delete_view(request, pk):
    """Deletes a lead record with confirmation."""
    lead = get_object_or_404(Lead, pk=pk)

    if request.method == 'POST':
        title = lead.title
        lead.delete()
        messages.success(request, f"Lead '{title}' has been removed.")
        return redirect('clients:lead_list')

    return render(request, 'clients/lead_confirm_delete.html', {
        'lead': lead,
        'page_title': f'Confirm Delete: {lead.title}'
    })


@login_required
@admin_hr_pm_required
def lead_convert_view(request, pk):
    """
    Converts a Lead into an official Client record:
    - Option 1: Create a brand new Client using the prospect's details.
    - Option 2: Associate with an existing Client in the system.
    Transitions Lead status to 'CONVERTED'.
    """
    lead = get_object_or_404(Lead, pk=pk)

    if lead.status == Lead.Status.CONVERTED and lead.converted_client:
        messages.info(request, f"This lead is already converted to client '{lead.converted_client.company_name}'.")
        return redirect('clients:detail', pk=lead.converted_client.pk)

    if request.method == 'POST':
        form = LeadConvertForm(request.POST)
        if form.is_valid():
            conv_type = form.cleaned_data['conversion_type']

            if conv_type == 'NEW_CLIENT':
                # Create brand new Client
                client = Client.objects.create(
                    client_id=form.cleaned_data['client_id'].upper(),
                    company_name=lead.organization_name,
                    contact_person=lead.contact_person,
                    email=lead.email,
                    phone=lead.phone,
                    industry=form.cleaned_data['industry'],
                    address=form.cleaned_data['address'],
                    registration_date=timezone.now().date()
                )
                messages.success(request, f"New Client '{client.company_name}' ({client.client_id}) created from lead!")
            else:
                # Link existing Client
                client = form.cleaned_data['existing_client']
                messages.success(request, f"Lead successfully linked to existing client '{client.company_name}'.")

            # Update lead record
            lead.status = Lead.Status.CONVERTED
            lead.converted_client = client
            lead.save()

            return redirect('clients:detail', pk=client.pk)
        else:
            messages.error(request, "Please resolve the errors below.")
    else:
        # Pre-fill client ID suggestion
        suggested_id = f"CLT-{lead.id:03d}"
        form = LeadConvertForm(initial={'client_id': suggested_id})

    return render(request, 'clients/lead_convert.html', {
        'lead': lead,
        'form': form,
        'page_title': f'Convert Lead: {lead.title}'
    })

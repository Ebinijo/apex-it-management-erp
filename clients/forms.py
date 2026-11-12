from django import forms
from .models import Client, Lead
from employees.models import EmployeeProfile

class ClientForm(forms.ModelForm):
    """Form to register or update corporate clients"""
    class Meta:
        model = Client
        fields = ['client_id', 'company_name', 'contact_person', 'email', 'phone', 'industry', 'website', 'address', 'registration_date']
        widgets = {
            'client_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CLT-101'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. FinTech Innovations Global'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Victoria Sterling'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contact@clientcompany.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 234-5678'}),
            'industry': forms.Select(attrs={'class': 'form-select'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.company.com'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Corporate Headquarters Address'}),
            'registration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_client_id(self):
        cid = self.cleaned_data.get('client_id', '').strip().upper()
        qs = Client.objects.filter(client_id__iexact=cid)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A client with this Client ID already exists.")
        return cid

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = Client.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Another client is already registered with this corporate email.")
        return email


class LeadForm(forms.ModelForm):
    """Form to create or update sales opportunity leads"""
    class Meta:
        model = Lead
        fields = [
            'lead_id', 'title', 'organization_name', 'contact_person',
            'email', 'phone', 'assigned_employee', 'lead_source',
            'status', 'description'
        ]
        widgets = {
            'lead_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. LEAD-201'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Core Banking Platform Redesign'}),
            'organization_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Nexa Financial Group'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Marcus Vance'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'm.vance@prospect.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 456-7890'}),
            'assigned_employee': forms.Select(attrs={'class': 'form-select'}),
            'lead_source': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Scope, timeline, client expectations...'}),
        }

    def clean_lead_id(self):
        lid = self.cleaned_data.get('lead_id', '').strip().upper()
        qs = Lead.objects.filter(lead_id__iexact=lid)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A lead with this ID already exists.")
        return lid


class LeadConvertForm(forms.Form):
    """
    Form to convert a sales Lead into an official Client record:
    Allows creating a new Client from lead data, or associating with an existing Client.
    """
    CONVERSION_CHOICES = [
        ('NEW_CLIENT', 'Create a Brand New Client Record'),
        ('EXISTING_CLIENT', 'Associate with an Existing Client Record'),
    ]

    conversion_type = forms.ChoiceField(
        choices=CONVERSION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='NEW_CLIENT'
    )
    # Fields for creating a new Client
    client_id = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CLT-301'}),
        help_text="Required if creating a new client."
    )
    industry = forms.ChoiceField(
        choices=Client.Industry.choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Headquarters address'}),
        required=False
    )
    # Field for linking to existing Client
    existing_client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select existing client if associating."
    )

    def clean(self):
        cleaned_data = super().clean()
        conv_type = cleaned_data.get('conversion_type')

        if conv_type == 'NEW_CLIENT':
            cid = cleaned_data.get('client_id', '').strip().upper()
            if not cid:
                self.add_error('client_id', "Please provide a unique Client ID for the new client record.")
            elif Client.objects.filter(client_id__iexact=cid).exists():
                self.add_error('client_id', f"Client ID '{cid}' is already in use.")
        elif conv_type == 'EXISTING_CLIENT':
            if not cleaned_data.get('existing_client'):
                self.add_error('existing_client', "Please select an existing client from the list.")

        return cleaned_data

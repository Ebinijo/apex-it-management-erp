from django import forms
from .models import Project
from clients.models import Client
from employees.models import EmployeeProfile
from accounts.models import User

class ProjectForm(forms.ModelForm):
    """Form to create and update company software projects"""
    class Meta:
        model = Project
        fields = [
            'project_id', 'name', 'client', 'project_manager',
            'team_members', 'start_date', 'deadline', 'status', 'description'
        ]
        widgets = {
            'project_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. PRJ-101'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Real-Time Payment Settlement Gateway'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'project_manager': forms.Select(attrs={'class': 'form-select'}),
            'team_members': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5',
                'help_text': 'Hold Ctrl (or Cmd on Mac) to select multiple developers.'
            }),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Project architecture, sprint goals and functional requirements...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter Project Manager choices to PM and Admin profiles
        self.fields['project_manager'].queryset = EmployeeProfile.objects.filter(
            user__role__in=[User.Role.PROJECT_MANAGER, User.Role.ADMIN]
        ).select_related('user')
        
        # Filter Team Members choices to Developers
        self.fields['team_members'].queryset = EmployeeProfile.objects.filter(
            user__role=User.Role.DEVELOPER
        ).select_related('user', 'department')

    def clean_project_id(self):
        pid = self.cleaned_data.get('project_id', '').strip().upper()
        qs = Project.objects.filter(project_id__iexact=pid)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A project with this Project ID already exists.")
        return pid

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        deadline = cleaned_data.get('deadline')
        if start and deadline:
            if deadline < start:
                self.add_error('deadline', "Project deadline cannot be earlier than start date.")
        return cleaned_data

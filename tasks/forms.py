from django import forms
from .models import Task, Bug
from projects.models import Project
from employees.models import EmployeeProfile
from accounts.models import User

class TaskForm(forms.ModelForm):
    """Form for Project Managers and Admins to create and manage sprint tasks"""
    class Meta:
        model = Task
        fields = [
            'task_id', 'title', 'project', 'assigned_developer',
            'priority', 'status', 'start_date', 'deadline', 'description'
        ]
        widgets = {
            'task_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. TSK-101'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Implement OAuth2 JWT Refresh Token Endpoint'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'assigned_developer': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Acceptance criteria, test cases, endpoint contract...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter assigned_developer to active developers
        self.fields['assigned_developer'].queryset = EmployeeProfile.objects.filter(
            user__role=User.Role.DEVELOPER
        ).select_related('user', 'department')

    def clean_task_id(self):
        tid = self.cleaned_data.get('task_id', '').strip().upper()
        qs = Task.objects.filter(task_id__iexact=tid)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A task with this Task ID already exists.")
        return tid

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        deadline = cleaned_data.get('deadline')
        if start and deadline:
            if deadline < start:
                self.add_error('deadline', "Task deadline cannot be earlier than start date.")
        return cleaned_data


class TaskStatusUpdateForm(forms.ModelForm):
    """Compact form allowing developers to quickly update task status"""
    class Meta:
        model = Task
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class BugReportForm(forms.ModelForm):
    """Form allowing developers and team members to log defects against a project"""
    class Meta:
        model = Bug
        fields = ['bug_id', 'title', 'project', 'priority', 'description']
        widgets = {
            'bug_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. BUG-101'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Race condition in concurrent database transaction ledger'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '1. Steps to reproduce\n2. Expected behavior\n3. Actual behavior / Stacktrace'}),
        }

    def clean_bug_id(self):
        bid = self.cleaned_data.get('bug_id', '').strip().upper()
        qs = Bug.objects.filter(bug_id__iexact=bid)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A bug with this Bug ID already exists.")
        return bid


class BugUpdateForm(forms.ModelForm):
    """Form for Project Managers to assign bugs and developers to document resolution"""
    class Meta:
        model = Bug
        fields = ['assigned_developer', 'priority', 'status', 'resolution_notes']
        widgets = {
            'assigned_developer': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'resolution_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Root cause explanation, commit hash or fix verification notes...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_developer'].queryset = EmployeeProfile.objects.filter(
            user__role=User.Role.DEVELOPER
        ).select_related('user', 'department')

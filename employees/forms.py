from django import forms
from django.utils import timezone
from accounts.models import User
from .models import Department, EmployeeProfile, LeaveRequest

class DepartmentForm(forms.ModelForm):
    """Form to create and edit company departments"""
    class Meta:
        model = Department
        fields = ['name', 'code', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Software Engineering'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ENG'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Department functions and responsibilities...'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        qs = Department.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A department with this name already exists.")
        return name

    def clean_code(self):
        code = self.cleaned_data.get('code', '').upper()
        qs = Department.objects.filter(code__iexact=code)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A department with this code already exists.")
        return code


class EmployeeCreateForm(forms.ModelForm):
    """
    Combined form allowing HR/Admin to create both the user account credentials
    and the detailed employee profile in a single operation.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unique Username'}),
        help_text="Login username"
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'corporate.email@company.com'}),
        help_text="Company email address"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Initial Temporary Password'}),
        help_text="Must be at least 6 characters"
    )
    role = forms.ChoiceField(
        choices=User.Role.choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Access tier across the platform"
    )

    class Meta:
        model = EmployeeProfile
        fields = [
            'employee_id', 'department', 'designation', 'gender',
            'phone', 'joining_date', 'skills', 'employment_status',
            'emergency_contact', 'address'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. EMP-101'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Full-Stack Developer'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 000-0000'}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. Python, Django, PostgreSQL, Docker, Git'}),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Name & Phone'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Residential Address'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean_employee_id(self):
        emp_id = self.cleaned_data.get('employee_id', '').strip().upper()
        if EmployeeProfile.objects.filter(employee_id__iexact=emp_id).exists():
            raise forms.ValidationError("This Employee ID is already assigned. Please use a unique ID.")
        return emp_id

    def save(self, commit=True):
        # 1. Create User instance
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            role=self.cleaned_data['role'],
            designation=self.cleaned_data['designation'],
            phone=self.cleaned_data['phone']
        )
        # 2. Create EmployeeProfile
        profile = super().save(commit=False)
        profile.user = user
        profile.employee_id = self.cleaned_data['employee_id'].upper()
        if commit:
            profile.save()
        return profile


class EmployeeUpdateForm(forms.ModelForm):
    """Form to update existing employee record and user details"""
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(choices=User.Role.choices, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = EmployeeProfile
        fields = [
            'department', 'designation', 'gender', 'phone',
            'joining_date', 'skills', 'employment_status',
            'emergency_contact', 'address'
        ]
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['role'].initial = self.instance.user.role

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user = self.instance.user
        if User.objects.filter(email__iexact=email).exclude(pk=user.pk).exists():
            raise forms.ValidationError("Another user is already registered with this email address.")
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        user.designation = profile.designation
        user.phone = profile.phone
        user.save()
        if commit:
            profile.save()
        return profile


class LeaveApplicationForm(forms.ModelForm):
    """Form for employees to apply for leave with date validation"""
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'State the reason and coverage plan for your absence...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if end_date < start_date:
                self.add_error('end_date', "Leave end date cannot be earlier than start date.")
        return cleaned_data


class LeaveReviewForm(forms.ModelForm):
    """Form for HR/Admin to approve or reject leave applications"""
    class Meta:
        model = LeaveRequest
        fields = ['status', 'admin_remarks']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Provide feedback or approval notes...'}),
        }

    def clean_status(self):
        status = self.cleaned_data.get('status')
        if status == LeaveRequest.Status.PENDING:
            raise forms.ValidationError("Please select either Approved or Rejected.")
        return status

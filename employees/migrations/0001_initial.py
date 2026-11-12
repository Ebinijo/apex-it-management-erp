from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Department name', max_length=100, unique=True)),
                ('code', models.CharField(help_text='Unique short code (e.g. ENG, QA, HR)', max_length=20, unique=True)),
                ('description', models.TextField(blank=True, help_text='Department responsibilities and scope')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Department',
                'verbose_name_plural': 'Departments',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='EmployeeProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_id', models.CharField(help_text='Unique Employee Identification Code (e.g. EMP-001)', max_length=20, unique=True)),
                ('designation', models.CharField(help_text='Official job title', max_length=100)),
                ('gender', models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other'), ('PREFER_NOT_TO_SAY', 'Prefer not to say')], default='PREFER_NOT_TO_SAY', max_length=20)),
                ('phone', models.CharField(blank=True, help_text='Contact number', max_length=20)),
                ('joining_date', models.DateField(default=django.utils.timezone.now, help_text='Date joined the organization')),
                ('skills', models.TextField(blank=True, help_text='Comma-separated technical competencies (e.g. Python, Django, Docker, AWS)')),
                ('employment_status', models.CharField(choices=[('FULL_TIME', 'Full-Time'), ('PART_TIME', 'Part-Time'), ('CONTRACT', 'Contractor'), ('INTERN', 'Intern'), ('RESIGNED', 'Resigned')], default='FULL_TIME', max_length=20)),
                ('emergency_contact', models.CharField(blank=True, help_text='Emergency contact person and phone', max_length=100)),
                ('address', models.TextField(blank=True, help_text='Residential postal address')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('department', models.ForeignKey(blank=True, help_text='Assigned company department', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employees', to='employees.department')),
                ('user', models.OneToOneField(help_text='Associated system user credentials', on_delete=django.db.models.deletion.CASCADE, related_name='employee_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Employee Profile',
                'verbose_name_plural': 'Employee Profiles',
                'ordering': ['employee_id'],
            },
        ),
        migrations.CreateModel(
            name='LeaveRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leave_type', models.CharField(choices=[('CASUAL', 'Casual Leave'), ('SICK', 'Sick / Medical Leave'), ('ANNUAL', 'Annual Paid Leave'), ('MATERNITY_PATERNITY', 'Maternity / Paternity Leave'), ('UNPAID', 'Leave Without Pay')], default='CASUAL', max_length=30)),
                ('start_date', models.DateField(help_text='First day of leave')),
                ('end_date', models.DateField(help_text='Last day of leave')),
                ('reason', models.TextField(help_text='Detailed justification for leave')),
                ('status', models.CharField(choices=[('PENDING', 'Pending Approval'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING', max_length=20)),
                ('admin_remarks', models.TextField(blank=True, help_text='Feedback or remarks from HR/Admin')),
                ('applied_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('employee', models.ForeignKey(help_text='Employee applying for leave', on_delete=django.db.models.deletion.CASCADE, related_name='leave_requests', to='employees.employeeprofile')),
                ('reviewed_by', models.ForeignKey(blank=True, help_text='HR or Admin who approved/rejected the request', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_leaves', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Leave Request',
                'verbose_name_plural': 'Leave Requests',
                'ordering': ['-applied_at'],
            },
        ),
    ]

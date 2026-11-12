from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0001_initial'),
        ('employees', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.CharField(help_text='Unique Task Identifier (e.g. TSK-001)', max_length=20, unique=True)),
                ('title', models.CharField(help_text='Actionable task title', max_length=150)),
                ('description', models.TextField(blank=True, help_text='Technical acceptance criteria and implementation details')),
                ('priority', models.CharField(choices=[('LOW', 'Low Priority'), ('MEDIUM', 'Medium Priority'), ('HIGH', 'High Priority'), ('CRITICAL', 'Critical / Urgent')], default='MEDIUM', max_length=20)),
                ('status', models.CharField(choices=[('TODO', 'To Do'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('BLOCKED', 'Blocked')], default='TODO', max_length=20)),
                ('start_date', models.DateField(default=django.utils.timezone.now, help_text='Task start date')),
                ('deadline', models.DateField(help_text='Target task completion deadline')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_developer', models.ForeignKey(blank=True, help_text='Assigned developer executing this work unit', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tasks', to='employees.employeeprofile')),
                ('created_by', models.ForeignKey(blank=True, help_text='Project Manager or Admin who created the task', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_tasks', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(help_text='Associated software project', on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='projects.project')),
            ],
            options={
                'verbose_name': 'Task',
                'verbose_name_plural': 'Tasks',
                'ordering': ['deadline', '-priority'],
            },
        ),
        migrations.CreateModel(
            name='Bug',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bug_id', models.CharField(help_text='Unique Bug Identifier (e.g. BUG-001)', max_length=20, unique=True)),
                ('title', models.CharField(help_text='Summary of defect or abnormal behavior', max_length=150)),
                ('description', models.TextField(help_text='Steps to reproduce, expected vs actual behavior, stack traces')),
                ('priority', models.CharField(choices=[('LOW', 'Low Severity'), ('MEDIUM', 'Medium Severity'), ('HIGH', 'High Severity'), ('CRITICAL', 'Critical Blocker')], default='HIGH', max_length=20)),
                ('status', models.CharField(choices=[('OPEN', 'Open'), ('IN_PROGRESS', 'In Progress'), ('RESOLVED', 'Resolved'), ('CLOSED', 'Closed')], default='OPEN', max_length=20)),
                ('reported_date', models.DateField(default=django.utils.timezone.now)),
                ('resolution_notes', models.TextField(blank=True, help_text='Root cause diagnosis, commit reference, or patch notes')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_developer', models.ForeignKey(blank=True, help_text='Developer tasked with investigating and fixing defect', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_bugs', to='employees.employeeprofile')),
                ('project', models.ForeignKey(help_text='Project in which defect was discovered', on_delete=django.db.models.deletion.CASCADE, related_name='bugs', to='projects.project')),
                ('reported_by', models.ForeignKey(blank=True, help_text='User/Developer who discovered and logged the issue', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reported_bugs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Bug Issue',
                'verbose_name_plural': 'Bug Issues',
                'ordering': ['-created_at'],
            },
        ),
    ]

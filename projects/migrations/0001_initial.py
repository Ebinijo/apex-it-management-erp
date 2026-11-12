from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0001_initial'),
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_id', models.CharField(help_text='Unique Project Identifier (e.g. PRJ-001)', max_length=20, unique=True)),
                ('name', models.CharField(help_text='Official Project Title', max_length=150)),
                ('description', models.TextField(blank=True, help_text='Detailed project requirements, architecture and deliverables')),
                ('start_date', models.DateField(default=django.utils.timezone.now, help_text='Sprint start date')),
                ('deadline', models.DateField(help_text='Target delivery deadline')),
                ('status', models.CharField(choices=[('PLANNING', 'Planning & Scoping'), ('IN_PROGRESS', 'In Progress'), ('TESTING', 'Testing & QA'), ('COMPLETED', 'Completed'), ('ON_HOLD', 'On Hold')], default='PLANNING', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(help_text='Contracted corporate client', on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='clients.client')),
                ('project_manager', models.ForeignKey(blank=True, help_text='Assigned Project Manager overseeing delivery', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_projects', to='employees.employeeprofile')),
                ('team_members', models.ManyToManyField(blank=True, help_text='Engineering team developers allocated to project', related_name='assigned_projects', to='employees.employeeprofile')),
            ],
            options={
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
                'ordering': ['-created_at'],
            },
        ),
    ]

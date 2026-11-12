from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_id', models.CharField(help_text='Unique Client Identifier (e.g. CLT-001)', max_length=20, unique=True)),
                ('company_name', models.CharField(help_text='Registered Corporate Entity Name', max_length=150)),
                ('contact_person', models.CharField(help_text='Primary stakeholder or point of contact', max_length=100)),
                ('email', models.EmailField(help_text='Official business correspondence email', max_length=254, unique=True)),
                ('phone', models.CharField(blank=True, help_text='Primary telephone number', max_length=25)),
                ('address', models.TextField(blank=True, help_text='Corporate headquarters address')),
                ('industry', models.CharField(choices=[('FINTECH', 'Financial Technology (FinTech)'), ('HEALTHCARE', 'Healthcare & Life Sciences'), ('ECOMMERCE', 'E-Commerce & Retail'), ('LOGISTICS', 'Supply Chain & Logistics'), ('EDUCATION', 'EdTech & Higher Education'), ('CYBERSECURITY', 'Cybersecurity & Defense'), ('TELECOM', 'Telecommunications'), ('MANUFACTURING', 'Industrial & Manufacturing'), ('MEDIA', 'Digital Media & Entertainment'), ('OTHER', 'Other Industry')], default='OTHER', help_text='Primary business vertical', max_length=30)),
                ('website', models.URLField(blank=True, help_text='Company website URL', null=True)),
                ('registration_date', models.DateField(default=django.utils.timezone.now, help_text='Date onboarded as an official client')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Client',
                'verbose_name_plural': 'Clients',
                'ordering': ['company_name'],
            },
        ),
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lead_id', models.CharField(help_text='Unique Lead Identifier (e.g. LEAD-001)', max_length=20, unique=True)),
                ('title', models.CharField(help_text='Opportunity summary or project scope', max_length=150)),
                ('organization_name', models.CharField(help_text='Prospect organization name', max_length=150)),
                ('contact_person', models.CharField(help_text='Prospect contact person', max_length=100)),
                ('email', models.EmailField(help_text='Contact email address', max_length=254)),
                ('phone', models.CharField(blank=True, help_text='Contact phone number', max_length=25)),
                ('lead_source', models.CharField(choices=[('WEBSITE', 'Website Contact Form'), ('REFERRAL', 'Client Referral'), ('LINKEDIN', 'LinkedIn / Social Outreach'), ('COLD_OUTREACH', 'Cold Call / Email'), ('CONFERENCE', 'Tech Conference / Trade Show'), ('PARTNER', 'Business Partner Network'), ('OTHER', 'Other Source')], default='WEBSITE', max_length=30)),
                ('description', models.TextField(blank=True, help_text='Opportunity requirements and background')),
                ('status', models.CharField(choices=[('NEW', 'New Opportunity'), ('CONTACTED', 'Contacted / Discovery'), ('CONVERTED', 'Converted to Client'), ('LOST', 'Lost / Closed')], default='NEW', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_employee', models.ForeignKey(blank=True, help_text='Account executive or technical lead assigned', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_leads', to='employees.employeeprofile')),
                ('converted_client', models.ForeignKey(blank=True, help_text='Associated Client record once converted', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='converted_from_leads', to='clients.client')),
            ],
            options={
                'verbose_name': 'Sales Lead',
                'verbose_name_plural': 'Sales Leads',
                'ordering': ['-created_at'],
            },
        ),
    ]

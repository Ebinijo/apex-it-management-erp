from django.db import models
from django.utils import timezone
from employees.models import EmployeeProfile

class Client(models.Model):
    """
    Corporate client organization engaging the IT company's services.
    """
    class Industry(models.TextChoices):
        FINTECH = 'FINTECH', 'Financial Technology (FinTech)'
        HEALTHCARE = 'HEALTHCARE', 'Healthcare & Life Sciences'
        ECOMMERCE = 'ECOMMERCE', 'E-Commerce & Retail'
        LOGISTICS = 'LOGISTICS', 'Supply Chain & Logistics'
        EDUCATION = 'EDUCATION', 'EdTech & Higher Education'
        CYBERSECURITY = 'CYBERSECURITY', 'Cybersecurity & Defense'
        TELECOM = 'TELECOM', 'Telecommunications'
        MANUFACTURING = 'MANUFACTURING', 'Industrial & Manufacturing'
        MEDIA = 'MEDIA', 'Digital Media & Entertainment'
        OTHER = 'OTHER', 'Other Industry'

    client_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique Client Identifier (e.g. CLT-001)"
    )
    company_name = models.CharField(max_length=150, help_text="Registered Corporate Entity Name")
    contact_person = models.CharField(max_length=100, help_text="Primary stakeholder or point of contact")
    email = models.EmailField(unique=True, help_text="Official business correspondence email")
    phone = models.CharField(max_length=25, blank=True, help_text="Primary telephone number")
    address = models.TextField(blank=True, help_text="Corporate headquarters address")
    industry = models.CharField(
        max_length=30,
        choices=Industry.choices,
        default=Industry.OTHER,
        help_text="Primary business vertical"
    )
    website = models.URLField(blank=True, null=True, help_text="Company website URL")
    registration_date = models.DateField(default=timezone.now, help_text="Date onboarded as an official client")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['company_name']
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return f"{self.company_name} ({self.client_id})"

    @property
    def active_projects_count(self):
        """Returns total projects associated with this client (Phase 4 integration)."""
        if hasattr(self, 'projects'):
            return self.projects.count()
        return 0


class Lead(models.Model):
    """
    Prospective client inquiry or business opportunity.
    """
    class Status(models.TextChoices):
        NEW = 'NEW', 'New Opportunity'
        CONTACTED = 'CONTACTED', 'Contacted / Discovery'
        CONVERTED = 'CONVERTED', 'Converted to Client'
        LOST = 'LOST', 'Lost / Closed'

    class Source(models.TextChoices):
        WEBSITE = 'WEBSITE', 'Website Contact Form'
        REFERRAL = 'REFERRAL', 'Client Referral'
        LINKEDIN = 'LINKEDIN', 'LinkedIn / Social Outreach'
        COLD_OUTREACH = 'COLD_OUTREACH', 'Cold Call / Email'
        CONFERENCE = 'CONFERENCE', 'Tech Conference / Trade Show'
        PARTNER = 'PARTNER', 'Business Partner Network'
        OTHER = 'OTHER', 'Other Source'

    lead_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique Lead Identifier (e.g. LEAD-001)"
    )
    title = models.CharField(max_length=150, help_text="Opportunity summary or project scope")
    organization_name = models.CharField(max_length=150, help_text="Prospect organization name")
    contact_person = models.CharField(max_length=100, help_text="Prospect contact person")
    email = models.EmailField(help_text="Contact email address")
    phone = models.CharField(max_length=25, blank=True, help_text="Contact phone number")
    
    assigned_employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_leads',
        help_text="Account executive or technical lead assigned"
    )
    lead_source = models.CharField(max_length=30, choices=Source.choices, default=Source.WEBSITE)
    description = models.TextField(blank=True, help_text="Opportunity requirements and background")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    
    converted_client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='converted_from_leads',
        help_text="Associated Client record once converted"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Sales Lead'
        verbose_name_plural = 'Sales Leads'

    def __str__(self):
        return f"{self.lead_id}: {self.title} - {self.organization_name} [{self.get_status_display()}]"

    @property
    def status_badge_class(self):
        badges = {
            self.Status.NEW: 'bg-primary',
            self.Status.CONTACTED: 'bg-warning text-dark',
            self.Status.CONVERTED: 'bg-success',
            self.Status.LOST: 'bg-danger',
        }
        return badges.get(self.status, 'bg-secondary')

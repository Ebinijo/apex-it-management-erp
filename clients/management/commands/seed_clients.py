from datetime import date
from django.core.management.base import BaseCommand
from clients.models import Client, Lead
from employees.models import EmployeeProfile

class Command(BaseCommand):
    help = 'Seeds initial corporate clients and sales opportunity leads'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Corporate Clients and Leads..."))

        # 1. Seed Clients
        clients_data = [
            {
                'client_id': 'CLT-001',
                'company_name': 'Nexus Financial Technologies',
                'contact_person': 'Victoria Sterling',
                'email': 'v.sterling@nexusfintech.com',
                'phone': '+1 (555) 301-4401',
                'industry': Client.Industry.FINTECH,
                'website': 'https://www.nexusfintech.example.com',
                'address': '100 Wall Street, Financial District, New York, NY',
                'registration_date': date(2023, 2, 10)
            },
            {
                'client_id': 'CLT-002',
                'company_name': 'BioHealth Cloud Systems',
                'contact_person': 'Dr. Robert Chen',
                'email': 'r.chen@biohealth.example.com',
                'phone': '+1 (555) 302-4402',
                'industry': Client.Industry.HEALTHCARE,
                'website': 'https://www.biohealth.example.com',
                'address': '450 Innovation Parkway, Cambridge, MA',
                'registration_date': date(2023, 4, 15)
            },
            {
                'client_id': 'CLT-003',
                'company_name': 'OmniCommerce Global Retail',
                'contact_person': 'Samantha Ray',
                'email': 'samantha@omnicommerce.example.com',
                'phone': '+1 (555) 303-4403',
                'industry': Client.Industry.ECOMMERCE,
                'website': 'https://www.omnicommerce.example.com',
                'address': '800 Market Street, San Francisco, CA',
                'registration_date': date(2023, 7, 22)
            },
            {
                'client_id': 'CLT-004',
                'company_name': 'Apex Logistics & Freight Hub',
                'contact_person': 'Arthur Pendelton',
                'email': 'arthur@apexlogistics.example.com',
                'phone': '+1 (555) 304-4404',
                'industry': Client.Industry.LOGISTICS,
                'website': 'https://www.apexlogistics.example.com',
                'address': '1200 Logistics Blvd, Dallas, TX',
                'registration_date': date(2023, 9, 5)
            },
        ]

        created_clients = {}
        for c in clients_data:
            client, created = Client.objects.get_or_create(client_id=c['client_id'], defaults=c)
            created_clients[c['client_id']] = client
            status = "Created" if created else "Found"
            self.stdout.write(self.style.SUCCESS(f"  [✓] {status} Client: {client.company_name} ({client.client_id})"))

        # 2. Get Employee for assignment
        account_exec = EmployeeProfile.objects.filter(designation__icontains='Project').first() or EmployeeProfile.objects.first()

        # 3. Seed Leads in various pipeline states
        leads_data = [
            {
                'lead_id': 'LEAD-001',
                'title': 'AI Fraud Prevention Core Service',
                'organization_name': 'Vanguard Global Banking',
                'contact_person': 'Michael Vance',
                'email': 'm.vance@vanguardbanking.example.com',
                'phone': '+1 (555) 901-1101',
                'lead_source': Lead.Source.WEBSITE,
                'status': Lead.Status.NEW,
                'description': 'Inquiry for high-throughput anomaly detection microservice to protect payment card transactions.',
                'assigned_employee': account_exec,
            },
            {
                'lead_id': 'LEAD-002',
                'title': 'HIPAA Telemedicine Patient Portal',
                'organization_name': 'Horizon Care Clinic Network',
                'contact_person': 'Evelyn Hayes',
                'email': 'e.hayes@horizoncare.example.com',
                'phone': '+1 (555) 902-1102',
                'lead_source': Lead.Source.REFERRAL,
                'status': Lead.Status.CONTACTED,
                'description': 'Telehealth scheduling and real-time WebRTC consultation platform requiring strict HIPAA compliance.',
                'assigned_employee': account_exec,
            },
            {
                'lead_id': 'LEAD-003',
                'title': 'Autonomous Fleet Route Optimizer',
                'organization_name': 'Apex Logistics & Freight Hub',
                'contact_person': 'Arthur Pendelton',
                'email': 'arthur@apexlogistics.example.com',
                'phone': '+1 (555) 304-4404',
                'lead_source': Lead.Source.LINKEDIN,
                'status': Lead.Status.CONVERTED,
                'description': 'IoT telemetry tracking and GPS routing optimization for long-haul trucking.',
                'assigned_employee': account_exec,
                'converted_client': created_clients.get('CLT-004'),
            },
            {
                'lead_id': 'LEAD-004',
                'title': 'Legacy Point-of-Sale Cloud Migration',
                'organization_name': 'Zenith Outlet Stores',
                'contact_person': 'Brian Miller',
                'email': 'brian@zenithstores.example.com',
                'phone': '+1 (555) 904-1104',
                'lead_source': Lead.Source.COLD_OUTREACH,
                'status': Lead.Status.LOST,
                'description': 'Client decided to defer ERP cloud migration due to internal fiscal year budget constraints.',
                'assigned_employee': account_exec,
            },
        ]

        for l in leads_data:
            lead, created = Lead.objects.get_or_create(lead_id=l['lead_id'], defaults=l)
            status = "Created" if created else "Found"
            self.stdout.write(self.style.SUCCESS(f"  [✓] {status} Lead: {lead.title} [{lead.get_status_display()}]"))

        self.stdout.write(self.style.SUCCESS("\nPhase 3 Client & Lead Pipeline seeding completed successfully!"))

from django.test import TestCase, Client as TestClient
from django.urls import reverse
from accounts.models import User
from employees.models import Department, EmployeeProfile
from clients.models import Client, Lead

class ClientAndLeadTests(TestCase):
    def setUp(self):
        self.client = TestClient()

        # Users and roles
        self.admin = User.objects.create_user('admin_c', 'admin_c@test.com', 'Pass123!', role=User.Role.ADMIN, is_staff=True, is_superuser=True)
        self.pm = User.objects.create_user('pm_c', 'pm_c@test.com', 'Pass123!', role=User.Role.PROJECT_MANAGER)
        self.dev = User.objects.create_user('dev_c', 'dev_c@test.com', 'Pass123!', role=User.Role.DEVELOPER)

        # Department & Employee for assignment
        self.dept = Department.objects.create(name='Sales Engineering', code='SALES')
        self.emp = EmployeeProfile.objects.create(
            user=self.pm,
            employee_id='EMP-PM-99',
            department=self.dept,
            designation='Account Director'
        )

        # Pre-seed one client
        self.test_client = Client.objects.create(
            client_id='CLT-900',
            company_name='Vanguard Software Systems',
            contact_person='Arthur Dent',
            email='arthur@vanguard.test',
            industry=Client.Industry.FINTECH
        )

        # Pre-seed one lead
        self.test_lead = Lead.objects.create(
            lead_id='LEAD-900',
            title='Core Banking Migration',
            organization_name='FinTech Global Partners',
            contact_person='Zaphod Beeblebrox',
            email='zaphod@fintechpartners.test',
            status=Lead.Status.NEW,
            assigned_employee=self.emp
        )

    def test_client_model_creation(self):
        """Client model string representation and properties."""
        self.assertEqual(str(self.test_client), "Vanguard Software Systems (CLT-900)")
        self.assertEqual(self.test_client.active_projects_count, 0)

    def test_lead_model_creation(self):
        """Lead model creates with default NEW status and helper badge."""
        self.assertEqual(self.test_lead.status, Lead.Status.NEW)
        self.assertEqual(self.test_lead.status_badge_class, 'bg-primary')

    def test_developer_cannot_access_clients(self):
        """Developer role is forbidden from accessing the Client module (403 Forbidden)."""
        self.client.login(username='dev_c', password='Pass123!')
        response = self.client.get(reverse('clients:list'))
        self.assertEqual(response.status_code, 403)

    def test_pm_can_access_clients_and_leads(self):
        """Project Manager can access Client and Lead pipeline."""
        self.client.login(username='pm_c', password='Pass123!')
        client_resp = self.client.get(reverse('clients:list'))
        self.assertEqual(client_resp.status_code, 200)

        lead_resp = self.client.get(reverse('clients:lead_list'))
        self.assertEqual(lead_resp.status_code, 200)

    def test_client_create_view(self):
        """Authorized user can onboard a new client."""
        self.client.login(username='pm_c', password='Pass123!')
        response = self.client.post(reverse('clients:create'), {
            'client_id': 'CLT-901',
            'company_name': 'Horizon Health Cloud',
            'contact_person': 'Dr. Marcus Welby',
            'email': 'welby@horizon.test',
            'phone': '+1 555-1234',
            'industry': Client.Industry.HEALTHCARE,
            'registration_date': '2024-01-15'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Client.objects.filter(client_id='CLT-901').exists())

    def test_client_search_and_filter(self):
        """Client search filters by company name and industry."""
        self.client.login(username='admin_c', password='Pass123!')
        response = self.client.get(reverse('clients:list') + '?q=Vanguard')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vanguard Software Systems')

    def test_lead_conversion_to_new_client(self):
        """Lead conversion creates a brand new Client and updates lead status to CONVERTED."""
        self.client.login(username='pm_c', password='Pass123!')
        response = self.client.post(reverse('clients:lead_convert', kwargs={'pk': self.test_lead.pk}), {
            'conversion_type': 'NEW_CLIENT',
            'client_id': 'CLT-CONV-01',
            'industry': Client.Industry.FINTECH,
            'address': '77 Enterprise Way'
        })
        self.assertEqual(response.status_code, 302)

        # Check lead was converted
        self.test_lead.refresh_from_db()
        self.assertEqual(self.test_lead.status, Lead.Status.CONVERTED)
        self.assertIsNotNone(self.test_lead.converted_client)
        self.assertEqual(self.test_lead.converted_client.client_id, 'CLT-CONV-01')
        self.assertEqual(self.test_lead.converted_client.company_name, 'FinTech Global Partners')

    def test_lead_conversion_to_existing_client(self):
        """Lead conversion can associate with an existing client."""
        lead2 = Lead.objects.create(
            lead_id='LEAD-901',
            title='Follow-up Expansion Contract',
            organization_name='Vanguard Software Systems',
            contact_person='Arthur Dent',
            email='arthur.expansion@vanguard.test'
        )
        self.client.login(username='admin_c', password='Pass123!')
        response = self.client.post(reverse('clients:lead_convert', kwargs={'pk': lead2.pk}), {
            'conversion_type': 'EXISTING_CLIENT',
            'existing_client': self.test_client.pk
        })
        self.assertEqual(response.status_code, 302)

        lead2.refresh_from_db()
        self.assertEqual(lead2.status, Lead.Status.CONVERTED)
        self.assertEqual(lead2.converted_client, self.test_client)

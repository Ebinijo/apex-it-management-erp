from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from employees.models import Department, EmployeeProfile, LeaveRequest
from clients.models import Client as CorporateClient
from projects.models import Project
from tasks.models import Task


class DashboardRoleRoutingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user('admin_u', 'admin@u.com', 'Pass123!', role=User.Role.ADMIN, is_staff=True, is_superuser=True)
        self.hr = User.objects.create_user('hr_u', 'hr@u.com', 'Pass123!', role=User.Role.HR)
        self.pm = User.objects.create_user('pm_u', 'pm@u.com', 'Pass123!', role=User.Role.PROJECT_MANAGER)
        self.dev = User.objects.create_user('dev_u', 'dev@u.com', 'Pass123!', role=User.Role.DEVELOPER)

    def test_unauthenticated_redirects_to_login(self):
        """Unauthenticated visitor to /dashboard/ is redirected to login page."""
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_admin_dashboard_routing(self):
        """Admin user visiting /dashboard/ is routed to executive admin panel."""
        self.client.login(username='admin_u', password='Pass123!')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard:admin'))
        panel_resp = self.client.get(reverse('dashboard:admin'))
        self.assertEqual(panel_resp.status_code, 200)
        self.assertContains(panel_resp, "Executive Admin Dashboard")

    def test_hr_dashboard_routing(self):
        """HR user visiting /dashboard/ is routed to HR panel."""
        self.client.login(username='hr_u', password='Pass123!')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard:hr'))

    def test_pm_dashboard_routing(self):
        """Project Manager visiting /dashboard/ is routed to PM panel."""
        self.client.login(username='pm_u', password='Pass123!')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard:pm'))

    def test_developer_dashboard_routing(self):
        """Developer visiting /dashboard/ is routed to Developer workspace panel."""
        self.client.login(username='dev_u', password='Pass123!')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard:developer'))

    def test_developer_accessing_admin_dashboard_denied(self):
        """Developer accessing /dashboard/admin-panel/ is denied with 403 Forbidden."""
        self.client.login(username='dev_u', password='Pass123!')
        response = self.client.get(reverse('dashboard:admin'))
        self.assertEqual(response.status_code, 403)


class DashboardReportsAndAnalyticsTests(TestCase):
    """Integration tests for the Reports Hub and CSV Export endpoints."""

    def setUp(self):
        self.client = Client()

        # Users
        self.admin = User.objects.create_superuser('admin_rep', 'admin@apex.com', 'Pass123!', role=User.Role.ADMIN)
        self.hr = User.objects.create_user('hr_rep', 'hr@apex.com', 'Pass123!', role=User.Role.HR)
        self.pm = User.objects.create_user('pm_rep', 'pm@apex.com', 'Pass123!', role=User.Role.PROJECT_MANAGER)
        self.dev = User.objects.create_user('dev_rep', 'dev@apex.com', 'Pass123!', role=User.Role.DEVELOPER)

        # Department & Employee
        self.dept = Department.objects.create(name='Cloud Architecture', code='ARC')
        self.emp = EmployeeProfile.objects.create(
            user=self.dev,
            employee_id='EMP-ARC-01',
            department=self.dept,
            designation='Cloud Architect',
            joining_date=date(2025, 1, 15),
            salary=110000.00
        )

        # Corporate Client & Project
        self.corp_client = CorporateClient.objects.create(
            company_name='Global Tech',
            client_code='CLT-GT-01',
            contact_person='Robert Lang',
            email='robert@globaltech.com'
        )
        self.project = Project.objects.create(
            project_id='PRJ-REP-01',
            name='Multi-Cloud Infrastructure',
            client=self.corp_client,
            status=Project.Status.IN_PROGRESS,
            start_date=date(2025, 2, 1),
            deadline=date(2025, 8, 1),
            budget=250000.00
        )

        # Sprint Task
        self.task = Task.objects.create(
            task_id='TSK-REP-01',
            title='Provision Terraform Cluster',
            project=self.project,
            assigned_developer=self.emp,
            created_by=self.admin,
            status=Task.Status.IN_PROGRESS,
            start_date=date(2025, 2, 1),
            deadline=date(2025, 3, 1)
        )

        # Leave Request
        self.leave = LeaveRequest.objects.create(
            employee=self.emp,
            leave_type=LeaveRequest.LeaveType.PAID,
            start_date=date(2025, 4, 1),
            end_date=date(2025, 4, 5),
            reason='Annual spring vacation',
            status=LeaveRequest.Status.APPROVED,
            reviewed_by=self.hr
        )

    def test_reports_hub_access_for_admin_and_pm(self):
        """Admin and PM can view the Reports Hub."""
        self.client.force_login(self.admin)
        response = self.client.get(reverse('dashboard:reports'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Company Records & Export Reports")

        self.client.force_login(self.pm)
        response = self.client.get(reverse('dashboard:reports'))
        self.assertEqual(response.status_code, 200)

    def test_reports_hub_restricted_for_developers(self):
        """Developers visiting /dashboard/reports/ are redirected with a message."""
        self.client.force_login(self.dev)
        response = self.client.get(reverse('dashboard:reports'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard:developer'))

    def test_export_employees_csv_success(self):
        """HR and Admin can download employee CSV data."""
        self.client.force_login(self.hr)
        response = self.client.get(reverse('dashboard:export_employees'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('attachment; filename="apex_employees_report_', response['Content-Disposition'])
        content = response.content.decode('utf-8')
        self.assertIn('EMP-ARC-01', content)
        self.assertIn('Cloud Architect', content)
        self.assertIn('110000.00', content)

    def test_export_employees_csv_denied_for_developer(self):
        """Developers cannot export employees CSV."""
        self.client.force_login(self.dev)
        response = self.client.get(reverse('dashboard:export_employees'))
        self.assertEqual(response.status_code, 302)

    def test_export_projects_csv_success(self):
        """PM can download project portfolio CSV data."""
        self.client.force_login(self.pm)
        response = self.client.get(reverse('dashboard:export_projects'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        content = response.content.decode('utf-8')
        self.assertIn('PRJ-REP-01', content)
        self.assertIn('Multi-Cloud Infrastructure', content)
        self.assertIn('250000.00', content)

    def test_export_tasks_csv_success(self):
        """PM can download tasks CSV data."""
        self.client.force_login(self.pm)
        response = self.client.get(reverse('dashboard:export_tasks'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('TSK-REP-01', content)
        self.assertIn('Provision Terraform Cluster', content)

    def test_export_leaves_csv_success(self):
        """HR can download leaves CSV data."""
        self.client.force_login(self.hr)
        response = self.client.get(reverse('dashboard:export_leaves'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('EMP-ARC-01', content)
        self.assertIn('Annual spring vacation', content)
        self.assertIn('Approved', content)

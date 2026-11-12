from datetime import date, timedelta
from django.test import TestCase, Client as TestClient
from django.urls import reverse
from django.core.exceptions import ValidationError
from accounts.models import User
from employees.models import Department, EmployeeProfile
from clients.models import Client
from projects.models import Project

class ProjectManagementTests(TestCase):
    def setUp(self):
        self.client = TestClient()

        # Users and roles
        self.admin = User.objects.create_user('admin_p', 'admin_p@test.com', 'Pass123!', role=User.Role.ADMIN, is_staff=True, is_superuser=True)
        self.pm_user = User.objects.create_user('pm_p', 'pm_p@test.com', 'Pass123!', role=User.Role.PROJECT_MANAGER)
        self.dev_user = User.objects.create_user('dev_p', 'dev_p@test.com', 'Pass123!', role=User.Role.DEVELOPER)

        # Department & Employee Profiles
        self.dept = Department.objects.create(name='Engineering Group', code='ENG-P')
        self.pm_profile = EmployeeProfile.objects.create(
            user=self.pm_user,
            employee_id='EMP-PM-01',
            department=self.dept,
            designation='Technical Project Manager'
        )
        self.dev_profile = EmployeeProfile.objects.create(
            user=self.dev_user,
            employee_id='EMP-DEV-01',
            department=self.dept,
            designation='Full-Stack Developer'
        )

        # Client
        self.test_client = Client.objects.create(
            client_id='CLT-PRJ-01',
            company_name='Apex Financial Systems',
            contact_person='Eleanor Vance',
            email='eleanor@apexfin.test'
        )

        # Sample Project
        today = date.today()
        self.test_project = Project.objects.create(
            project_id='PRJ-TEST-01',
            name='Core Banking Payment Rails',
            client=self.test_client,
            project_manager=self.pm_profile,
            start_date=today,
            deadline=today + timedelta(days=60),
            status=Project.Status.IN_PROGRESS
        )
        self.test_project.team_members.add(self.dev_profile)

    def test_project_model_creation_and_string(self):
        """Project model string representation and basic properties."""
        self.assertEqual(str(self.test_project), "PRJ-TEST-01 - Core Banking Payment Rails (Apex Financial Systems)")
        # If no tasks exist, progress must return 0%
        self.assertEqual(self.test_project.progress_percentage, 0)
        self.assertEqual(self.test_project.status_badge_class, 'bg-primary')

    def test_deadline_before_start_date_invalid(self):
        """Project deadline earlier than start date must raise ValidationError."""
        start = date.today()
        deadline = start - timedelta(days=5)
        project = Project(
            project_id='PRJ-ERR-01',
            name='Invalid Project Timeline',
            client=self.test_client,
            start_date=start,
            deadline=deadline
        )
        with self.assertRaises(ValidationError):
            project.clean()

    def test_developer_cannot_create_project(self):
        """Developer role is forbidden from creating new projects (403 Forbidden)."""
        self.client.login(username='dev_p', password='Pass123!')
        response = self.client.get(reverse('projects:create'))
        self.assertEqual(response.status_code, 403)

    def test_pm_can_create_project(self):
        """Project Manager can create new project with client and team."""
        self.client.login(username='pm_p', password='Pass123!')
        start = date.today()
        deadline = start + timedelta(days=45)
        response = self.client.post(reverse('projects:create'), {
            'project_id': 'PRJ-NEW-02',
            'name': 'Telehealth Mobile App API',
            'client': self.test_client.pk,
            'project_manager': self.pm_profile.pk,
            'team_members': [self.dev_profile.pk],
            'start_date': str(start),
            'deadline': str(deadline),
            'status': Project.Status.PLANNING,
            'description': 'Mobile backend microservices.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(project_id='PRJ-NEW-02').exists())

    def test_project_search_and_filter(self):
        """Project list search filters by name."""
        self.client.login(username='dev_p', password='Pass123!')
        response = self.client.get(reverse('projects:list') + '?q=Payment')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Core Banking Payment Rails')

    def test_developer_can_view_project_detail(self):
        """Developer can view project details and delivery timeline."""
        self.client.login(username='dev_p', password='Pass123!')
        response = self.client.get(reverse('projects:detail', kwargs={'pk': self.test_project.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Core Banking Payment Rails')
        self.assertContains(response, 'Apex Financial Systems')
        self.assertContains(response, '0%')  # Verified 0% progress when no tasks

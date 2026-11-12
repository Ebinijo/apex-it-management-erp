from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import User
from employees.models import Department, EmployeeProfile
from clients.models import Client as CorporateClient
from projects.models import Project
from tasks.models import Task, Bug


class TaskAndBugModelTests(TestCase):
    """Unit tests for Task and Bug data models, validations, and project progress interplay."""

    def setUp(self):
        # Admin & Developer users
        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin@apex.com',
            password='Password@123',
            role=User.Role.ADMIN
        )
        self.dev_user = User.objects.create_user(
            username='dev_tester',
            email='dev@apex.com',
            password='Password@123',
            role=User.Role.DEVELOPER
        )
        self.dept = Department.objects.create(name='Engineering', code='ENG')
        self.dev_profile = EmployeeProfile.objects.create(
            user=self.dev_user,
            employee_id='EMP-TEST-01',
            department=self.dept,
            designation='Software Engineer',
            joining_date=date(2025, 1, 1),
            salary=85000.00
        )
        self.corp_client = CorporateClient.objects.create(
            company_name='Apex Financial Systems',
            client_code='CLT-TEST-01',
            contact_person='Marcus Vance',
            email='marcus@apexfin.com',
            phone='+1-555-0199'
        )
        self.project = Project.objects.create(
            project_id='PRJ-TEST-01',
            name='Cloud Banking API',
            client=self.corp_client,
            status=Project.Status.IN_PROGRESS,
            start_date=timezone.now().date(),
            deadline=timezone.now().date() + timedelta(days=30),
            budget=150000.00
        )
        self.project.assigned_developers.add(self.dev_profile)

    def test_task_creation_and_overdue_property(self):
        """Test task creation and overdue calculation."""
        today = timezone.now().date()
        task = Task.objects.create(
            task_id='TSK-001',
            title='Implement JWT auth',
            project=self.project,
            assigned_developer=self.dev_profile,
            created_by=self.admin_user,
            priority=Task.Priority.HIGH,
            status=Task.Status.TODO,
            start_date=today - timedelta(days=10),
            deadline=today - timedelta(days=2) # In past -> Overdue!
        )
        self.assertEqual(task.status_badge_class, 'bg-secondary')
        self.assertEqual(task.priority_badge_class, 'bg-warning text-dark')
        self.assertTrue(task.is_overdue)

        # Mark completed -> Should no longer be overdue
        task.status = Task.Status.COMPLETED
        task.save()
        self.assertFalse(task.is_overdue)

    def test_task_date_validation(self):
        """Task deadline cannot precede start date."""
        today = timezone.now().date()
        with self.assertRaises(ValidationError):
            task = Task(
                task_id='TSK-INVALID',
                title='Invalid timeline task',
                project=self.project,
                start_date=today,
                deadline=today - timedelta(days=5) # Earlier than start
            )
            task.clean()

    def test_dynamic_project_progress_calculation(self):
        """Verifies that completed tasks dynamically increase project progress percentage."""
        today = timezone.now().date()
        # 0 tasks initially -> 0%
        self.assertEqual(self.project.progress_percentage, 0)

        # Create 2 tasks
        t1 = Task.objects.create(
            task_id='TSK-PROG-1',
            title='Task 1',
            project=self.project,
            assigned_developer=self.dev_profile,
            status=Task.Status.COMPLETED,
            start_date=today,
            deadline=today + timedelta(days=10)
        )
        t2 = Task.objects.create(
            task_id='TSK-PROG-2',
            title='Task 2',
            project=self.project,
            assigned_developer=self.dev_profile,
            status=Task.Status.TODO,
            start_date=today,
            deadline=today + timedelta(days=10)
        )
        # 1 out of 2 completed -> 50%
        self.assertEqual(self.project.progress_percentage, 50)

        # Complete second task -> 100%
        t2.status = Task.Status.COMPLETED
        t2.save()
        self.assertEqual(self.project.progress_percentage, 100)

    def test_bug_creation_and_resolution(self):
        """Test bug issue reporting and status workflow."""
        bug = Bug.objects.create(
            bug_id='BUG-001',
            title='Memory leak in session worker',
            project=self.project,
            reported_by=self.admin_user,
            assigned_developer=self.dev_profile,
            priority=Bug.Priority.CRITICAL,
            status=Bug.Status.OPEN,
            description='Heap allocation increases monotonically under concurrent load.'
        )
        self.assertEqual(bug.status_badge_class, 'bg-danger')
        self.assertEqual(bug.priority_badge_class, 'bg-danger text-white')

        # Update resolution
        bug.status = Bug.Status.RESOLVED
        bug.resolution_notes = 'Replaced circular reference with weakref dict.'
        bug.save()
        self.assertEqual(bug.status, Bug.Status.RESOLVED)
        self.assertEqual(bug.status_badge_class, 'bg-success')


class TaskAndBugViewTests(TestCase):
    """Integration tests for Task & Bug views and Role-Based Access Control."""

    def setUp(self):
        self.client = Client()

        # Admin user
        self.admin_user = User.objects.create_superuser(
            username='admin_user',
            email='admin@apex.com',
            password='Password@123',
            role=User.Role.ADMIN
        )

        # Project Manager user
        self.pm_user = User.objects.create_user(
            username='pm_manager',
            email='pm@apex.com',
            password='Password@123',
            role=User.Role.PROJECT_MANAGER
        )
        self.dept = Department.objects.create(name='Delivery', code='DEL')
        self.pm_profile = EmployeeProfile.objects.create(
            user=self.pm_user,
            employee_id='EMP-PM-01',
            department=self.dept,
            designation='Senior PM',
            joining_date=date(2024, 1, 1),
            salary=95000.00
        )

        # Developer 1
        self.dev1_user = User.objects.create_user(
            username='dev_user_1',
            email='dev1@apex.com',
            password='Password@123',
            role=User.Role.DEVELOPER
        )
        self.dev1_profile = EmployeeProfile.objects.create(
            user=self.dev1_user,
            employee_id='EMP-DEV-01',
            department=self.dept,
            designation='Full Stack Dev',
            joining_date=date(2025, 2, 1),
            salary=80000.00
        )

        # Developer 2
        self.dev2_user = User.objects.create_user(
            username='dev_user_2',
            email='dev2@apex.com',
            password='Password@123',
            role=User.Role.DEVELOPER
        )
        self.dev2_profile = EmployeeProfile.objects.create(
            user=self.dev2_user,
            employee_id='EMP-DEV-02',
            department=self.dept,
            designation='Frontend Dev',
            joining_date=date(2025, 3, 1),
            salary=78000.00
        )

        # Corporate Client & Project
        self.corp_client = CorporateClient.objects.create(
            company_name='FinTech Innovations',
            client_code='CLT-FT-01',
            contact_person='Alice Smith',
            email='alice@fintech.com',
            phone='+1-555-0800'
        )
        self.project = Project.objects.create(
            project_id='PRJ-FT-01',
            name='Payment Gateway Engine',
            client=self.corp_client,
            project_manager=self.pm_profile,
            status=Project.Status.IN_PROGRESS,
            start_date=timezone.now().date(),
            deadline=timezone.now().date() + timedelta(days=60),
            budget=200000.00
        )
        self.project.assigned_developers.add(self.dev1_profile, self.dev2_profile)

        # Task assigned to Dev 1
        self.today = timezone.now().date()
        self.task1 = Task.objects.create(
            task_id='TSK-GATEWAY-1',
            title='Implement Stripe Webhook',
            project=self.project,
            assigned_developer=self.dev1_profile,
            created_by=self.pm_user,
            priority=Task.Priority.HIGH,
            status=Task.Status.TODO,
            start_date=self.today,
            deadline=self.today + timedelta(days=14),
            description='Validate signatures and process charge events.'
        )

    def test_task_list_access(self):
        """Authenticated users can view the task list."""
        self.client.force_login(self.dev1_user)
        response = self.client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Implement Stripe Webhook')

    def test_task_creation_by_pm(self):
        """PM can successfully create a new task."""
        self.client.force_login(self.pm_user)
        url = reverse('tasks:create')
        post_data = {
            'task_id': 'TSK-GATEWAY-2',
            'title': 'Setup PayPal Sandbox Integration',
            'project': self.project.pk,
            'assigned_developer': self.dev2_profile.pk,
            'priority': Task.Priority.MEDIUM,
            'status': Task.Status.TODO,
            'start_date': str(self.today),
            'deadline': str(self.today + timedelta(days=15)),
            'description': 'Configure OAuth keys and sandbox test buyer accounts.'
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(task_id='TSK-GATEWAY-2').exists())

    def test_task_creation_forbidden_for_developer(self):
        """Developers cannot access task creation view (reserved for Admin and PM)."""
        self.client.force_login(self.dev1_user)
        response = self.client.get(reverse('tasks:create'))
        # Should redirect with permission error
        self.assertEqual(response.status_code, 302)

    def test_developer_status_transition(self):
        """Assigned developer can transition their task status from TODO to IN_PROGRESS."""
        self.client.force_login(self.dev1_user)
        url = reverse('tasks:status_update', kwargs={'pk': self.task1.pk})
        response = self.client.post(url, {'status': Task.Status.IN_PROGRESS})
        self.assertEqual(response.status_code, 302)

        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, Task.Status.IN_PROGRESS)

    def test_developer_cannot_update_other_developers_task(self):
        """Developer 2 cannot update status on Developer 1's assigned task."""
        self.client.force_login(self.dev2_user)
        url = reverse('tasks:status_update', kwargs={'pk': self.task1.pk})
        response = self.client.post(url, {'status': Task.Status.COMPLETED})
        self.assertEqual(response.status_code, 302)

        self.task1.refresh_from_db()
        # Must still be TODO!
        self.assertEqual(self.task1.status, Task.Status.TODO)

    def test_bug_reporting_by_developer(self):
        """Any authenticated user (including developer) can report a bug."""
        self.client.force_login(self.dev1_user)
        url = reverse('tasks:bug_report')
        post_data = {
            'bug_id': 'BUG-GATEWAY-1',
            'title': 'Webhook 500 error on expired idempotency key',
            'project': self.project.pk,
            'priority': Bug.Priority.HIGH,
            'description': 'When client submits duplicate payload with expired timestamp, unhandled KeyError is thrown.'
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Bug.objects.filter(bug_id='BUG-GATEWAY-1').exists())
        bug = Bug.objects.get(bug_id='BUG-GATEWAY-1')
        self.assertEqual(bug.reported_by, self.dev1_user)
        self.assertEqual(bug.status, Bug.Status.OPEN)

    def test_bug_triage_by_pm(self):
        """PM assigns developer and sets resolution notes on bug."""
        bug = Bug.objects.create(
            bug_id='BUG-GATEWAY-2',
            title='Null cursor on paginated transaction endpoint',
            project=self.project,
            reported_by=self.dev1_user,
            priority=Bug.Priority.HIGH,
            status=Bug.Status.OPEN,
            description='Page 2 returns 400 when cursor is missing.'
        )
        self.client.force_login(self.pm_user)
        url = reverse('tasks:bug_edit', kwargs={'pk': bug.pk})
        post_data = {
            'assigned_developer': self.dev1_profile.pk,
            'priority': Bug.Priority.HIGH,
            'status': Bug.Status.RESOLVED,
            'resolution_notes': 'Added default cursor fallback.'
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)

        bug.refresh_from_db()
        self.assertEqual(bug.assigned_developer, self.dev1_profile)
        self.assertEqual(bug.status, Bug.Status.RESOLVED)
        self.assertEqual(bug.resolution_notes, 'Added default cursor fallback.')

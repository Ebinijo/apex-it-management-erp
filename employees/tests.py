from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from accounts.models import User
from employees.models import Department, EmployeeProfile, LeaveRequest

class EmployeeAndLeaveTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create department
        self.dept_eng = Department.objects.create(name='Engineering', code='ENG', description='Software dev')
        self.dept_hr = Department.objects.create(name='Human Resources', code='HR', description='People ops')

        # Create Admin
        self.admin = User.objects.create_user(
            username='admin_emp',
            email='admin@corp.com',
            password='Password123!',
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True
        )

        # Create HR Manager
        self.hr = User.objects.create_user(
            username='hr_emp',
            email='hr@corp.com',
            password='Password123!',
            role=User.Role.HR
        )
        self.hr_profile = EmployeeProfile.objects.create(
            user=self.hr,
            employee_id='EMP-HR-01',
            department=self.dept_hr,
            designation='HR Manager',
            phone='+1 555-001'
        )

        # Create Developer
        self.dev = User.objects.create_user(
            username='dev_emp',
            email='dev@corp.com',
            password='Password123!',
            role=User.Role.DEVELOPER
        )
        self.dev_profile = EmployeeProfile.objects.create(
            user=self.dev,
            employee_id='EMP-DEV-01',
            department=self.dept_eng,
            designation='Python Developer',
            skills='Python, Django, PostgreSQL, Docker',
            phone='+1 555-002'
        )

    def test_department_creation_and_count(self):
        """Department creates cleanly and calculates headcount count."""
        self.assertEqual(self.dept_eng.employee_count, 1)
        self.assertEqual(self.dept_hr.employee_count, 1)
        self.assertEqual(str(self.dept_eng), "Engineering (ENG)")

    def test_employee_profile_properties(self):
        """Employee profile helper properties return accurate values."""
        self.assertEqual(self.dev_profile.full_name, 'dev_emp')
        self.assertEqual(self.dev_profile.email, 'dev@corp.com')
        self.assertEqual(len(self.dev_profile.skills_list), 4)
        self.assertIn('Python', self.dev_profile.skills_list)
        self.assertIn('Docker', self.dev_profile.skills_list)

    def test_leave_end_date_before_start_date_invalid(self):
        """Leave with end_date earlier than start_date must raise ValidationError."""
        start = date.today()
        end = start - timedelta(days=2)
        leave = LeaveRequest(
            employee=self.dev_profile,
            leave_type=LeaveRequest.LeaveType.CASUAL,
            start_date=start,
            end_date=end,
            reason="Invalid dates test"
        )
        with self.assertRaises(ValidationError):
            leave.clean()

    def test_leave_duration_calculation(self):
        """Leave duration days must calculate inclusive calendar days."""
        start = date.today()
        end = start + timedelta(days=4)
        leave = LeaveRequest.objects.create(
            employee=self.dev_profile,
            leave_type=LeaveRequest.LeaveType.ANNUAL,
            start_date=start,
            end_date=end,
            reason="Annual trip"
        )
        self.assertEqual(leave.duration_days, 5)

    def test_self_approval_prevention(self):
        """Employees are strictly prohibited from approving their own leave."""
        start = date.today()
        end = start + timedelta(days=1)
        leave = LeaveRequest.objects.create(
            employee=self.hr_profile,
            leave_type=LeaveRequest.LeaveType.CASUAL,
            start_date=start,
            end_date=end,
            reason="HR manager personal day"
        )
        leave.reviewed_by = self.hr  # Self approval attempt
        with self.assertRaises(ValidationError):
            leave.clean()

    def test_developer_cannot_create_employee(self):
        """Developer role is forbidden from registering new employees (403 Forbidden)."""
        self.client.login(username='dev_emp', password='Password123!')
        response = self.client.get(reverse('employees:create'))
        self.assertEqual(response.status_code, 403)

    def test_hr_can_create_employee(self):
        """HR Manager can create employee."""
        self.client.login(username='hr_emp', password='Password123!')
        response = self.client.post(reverse('employees:create'), {
            'username': 'new_candidate',
            'first_name': 'Candidate',
            'last_name': 'One',
            'email': 'candidate1@corp.com',
            'password': 'Password123!',
            'role': User.Role.DEVELOPER,
            'employee_id': 'EMP-NEW-99',
            'department': self.dept_eng.id,
            'designation': 'Junior Engineer',
            'gender': EmployeeProfile.Gender.MALE,
            'joining_date': str(date.today()),
            'skills': 'JavaScript, CSS',
            'employment_status': EmployeeProfile.EmploymentStatus.FULL_TIME
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(EmployeeProfile.objects.filter(employee_id='EMP-NEW-99').exists())

    def test_developer_can_apply_for_leave(self):
        """Developer can submit a leave application."""
        self.client.login(username='dev_emp', password='Password123!')
        start = date.today() + timedelta(days=3)
        end = date.today() + timedelta(days=4)
        response = self.client.post(reverse('employees:leave_apply'), {
            'leave_type': LeaveRequest.LeaveType.CASUAL,
            'start_date': str(start),
            'end_date': str(end),
            'reason': 'Attending family wedding.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(LeaveRequest.objects.filter(employee=self.dev_profile, reason='Attending family wedding.').exists())

    def test_hr_can_approve_developer_leave(self):
        """HR Manager can approve developer's leave request."""
        leave = LeaveRequest.objects.create(
            employee=self.dev_profile,
            leave_type=LeaveRequest.LeaveType.CASUAL,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            reason="Doctor visit"
        )
        self.client.login(username='hr_emp', password='Password123!')
        response = self.client.post(reverse('employees:leave_review', kwargs={'pk': leave.pk}), {
            'action': 'APPROVE',
            'admin_remarks': 'Approved by HR Director'
        })
        self.assertEqual(response.status_code, 302)
        leave.refresh_from_db()
        self.assertEqual(leave.status, LeaveRequest.Status.APPROVED)
        self.assertEqual(leave.reviewed_by, self.hr)

    def test_employee_search_and_filter(self):
        """Verify search query filters employees accurately."""
        self.client.login(username='dev_emp', password='Password123!')
        response = self.client.get(reverse('employees:list') + '?q=Python')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'EMP-DEV-01')

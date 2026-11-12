from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from employees.models import Department, EmployeeProfile, LeaveRequest

class Command(BaseCommand):
    help = 'Seeds departments, employee profiles, and sample leave requests'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Departments & Workforce data..."))

        # 1. Seed Departments
        dept_data = [
            {'name': 'Software Engineering', 'code': 'ENG', 'description': 'Full-stack software development, architectural design and platform maintenance.'},
            {'name': 'Quality Assurance', 'code': 'QA', 'description': 'Manual and automated testing, regression suites, and bug triaging.'},
            {'name': 'Human Resources', 'code': 'HR', 'description': 'Workforce talent acquisition, compensation, compliance and employee welfare.'},
            {'name': 'Product & UI/UX Design', 'code': 'PROD', 'description': 'User research, wireframing, interface prototypes and design systems.'},
            {'name': 'Cloud Infrastructure & DevOps', 'code': 'OPS', 'description': 'CI/CD automation, cloud architecture, system reliability and container orchestration.'},
        ]

        depts = {}
        for d in dept_data:
            dept, _ = Department.objects.get_or_create(code=d['code'], defaults=d)
            depts[d['code']] = dept
            self.stdout.write(self.style.SUCCESS(f"  [✓] Department: {dept.name} ({dept.code})"))

        # 2. Seed Employee Profiles for existing users
        profiles_map = [
            ('admin', 'EMP-001', 'ENG', 'Chief Technology Officer', 'MALE', 'Python, Django, AWS, Distributed Systems, Architecture', date(2021, 1, 15)),
            ('hr_manager', 'EMP-002', 'HR', 'HR Director', 'FEMALE', 'Talent Acquisition, Performance Mgmt, Labor Law, Strategic HR', date(2021, 3, 1)),
            ('pm_john', 'EMP-003', 'ENG', 'Senior Project Manager', 'MALE', 'Agile, Scrum, JIRA, Client Relations, Sprint Planning', date(2021, 6, 10)),
            ('dev_alex', 'EMP-004', 'ENG', 'Senior Full-Stack Engineer', 'MALE', 'Python, Django, React, PostgreSQL, Docker, Redis', date(2022, 2, 20)),
            ('dev_priya', 'EMP-005', 'ENG', 'Backend Python Specialist', 'FEMALE', 'Python, FastAPI, Django, Celery, REST APIs, GraphQL', date(2022, 5, 14)),
        ]

        for username, emp_id, dept_code, desig, gender, skills, join_date in profiles_map:
            try:
                user = User.objects.get(username=username)
                profile, created = EmployeeProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'employee_id': emp_id,
                        'department': depts[dept_code],
                        'designation': desig,
                        'gender': gender,
                        'phone': user.phone or '+1 (555) 000-1111',
                        'joining_date': join_date,
                        'skills': skills,
                        'employment_status': EmployeeProfile.EmploymentStatus.FULL_TIME,
                        'emergency_contact': 'Family Contact (+1 555-999-0000)',
                        'address': 'Tech Hub Tower, Silicon Boulevard'
                    }
                )
                status_txt = "Created" if created else "Found"
                self.stdout.write(self.style.SUCCESS(f"  [✓] {status_txt} Profile: {profile.employee_id} - {user.username}"))
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  [!] User '{username}' does not exist, skipping."))

        # 3. Seed additional employee
        extra_user, u_created = User.objects.get_or_create(
            username='qa_sam',
            defaults={
                'email': 'sam.qa@company.com',
                'first_name': 'Sam',
                'last_name': 'Miller',
                'role': User.Role.DEVELOPER,
                'designation': 'QA Automation Lead',
                'phone': '+1 (555) 777-8888',
                'is_staff': False
            }
        )
        if u_created:
            extra_user.set_password('dev123')
            extra_user.save()

        EmployeeProfile.objects.get_or_create(
            user=extra_user,
            defaults={
                'employee_id': 'EMP-006',
                'department': depts['QA'],
                'designation': 'QA Automation Lead',
                'gender': 'MALE',
                'phone': '+1 (555) 777-8888',
                'joining_date': date(2023, 1, 10),
                'skills': 'Selenium, PyTest, Cypress, Bugzilla, Postman, CI/CD',
                'employment_status': EmployeeProfile.EmploymentStatus.FULL_TIME,
                'emergency_contact': 'Linda Miller (+1 555-444-2222)'
            }
        )
        self.stdout.write(self.style.SUCCESS("  [✓] Additional QA Specialist 'qa_sam' provisioned."))

        # 4. Seed Sample Leave Applications
        hr_user = User.objects.filter(role=User.Role.HR).first()
        dev_profile = EmployeeProfile.objects.filter(user__username='dev_alex').first()
        priya_profile = EmployeeProfile.objects.filter(user__username='dev_priya').first()

        today = timezone.now().date()

        if dev_profile:
            LeaveRequest.objects.get_or_create(
                employee=dev_profile,
                start_date=today + timedelta(days=5),
                end_date=today + timedelta(days=7),
                defaults={
                    'leave_type': LeaveRequest.LeaveType.ANNUAL,
                    'reason': 'Family vacation trip scheduled in advance. All sprint tasks handed off.',
                    'status': LeaveRequest.Status.PENDING,
                }
            )
            self.stdout.write(self.style.SUCCESS("  [✓] Sample Pending Leave created for dev_alex"))

        if priya_profile:
            LeaveRequest.objects.get_or_create(
                employee=priya_profile,
                start_date=today - timedelta(days=10),
                end_date=today - timedelta(days=9),
                defaults={
                    'leave_type': LeaveRequest.LeaveType.SICK,
                    'reason': 'Viral fever and doctor consultation.',
                    'status': LeaveRequest.Status.APPROVED,
                    'reviewed_by': hr_user,
                    'admin_remarks': 'Approved. Medical certificate submitted.',
                    'reviewed_at': timezone.now() - timedelta(days=10)
                }
            )
            self.stdout.write(self.style.SUCCESS("  [✓] Sample Approved Leave created for dev_priya"))

        self.stdout.write(self.style.SUCCESS("\nPhase 2 Workforce & Leave seeding completed successfully!"))

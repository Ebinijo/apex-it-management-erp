from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Seeds initial demonstration users for all four enterprise roles'

    def handle(self, *args, **options):
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@company.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': User.Role.ADMIN,
                'designation': 'Chief Technology Officer',
                'phone': '+1 (555) 100-0001',
                'is_staff': True,
                'is_superuser': True,
                'password': 'admin123'
            },
            {
                'username': 'hr_manager',
                'email': 'hr@company.com',
                'first_name': 'Sarah',
                'last_name': 'Jenkins',
                'role': User.Role.HR,
                'designation': 'Head of Human Resources',
                'phone': '+1 (555) 200-0002',
                'is_staff': False,
                'is_superuser': False,
                'password': 'hr123'
            },
            {
                'username': 'pm_john',
                'email': 'pm.john@company.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': User.Role.PROJECT_MANAGER,
                'designation': 'Senior Project Lead',
                'phone': '+1 (555) 300-0003',
                'is_staff': False,
                'is_superuser': False,
                'password': 'pm123'
            },
            {
                'username': 'dev_alex',
                'email': 'alex.turner@company.com',
                'first_name': 'Alex',
                'last_name': 'Turner',
                'role': User.Role.DEVELOPER,
                'designation': 'Full-Stack Software Engineer',
                'phone': '+1 (555) 400-0004',
                'is_staff': False,
                'is_superuser': False,
                'password': 'dev123'
            },
            {
                'username': 'dev_priya',
                'email': 'priya.sharma@company.com',
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'role': User.Role.DEVELOPER,
                'designation': 'Backend Python Specialist',
                'phone': '+1 (555) 400-0005',
                'is_staff': False,
                'is_superuser': False,
                'password': 'dev123'
            },
        ]

        self.stdout.write(self.style.NOTICE("Seeding demonstration users..."))

        for u in users_data:
            user, created = User.objects.get_or_create(
                username=u['username'],
                defaults={
                    'email': u['email'],
                    'first_name': u['first_name'],
                    'last_name': u['last_name'],
                    'role': u['role'],
                    'designation': u['designation'],
                    'phone': u['phone'],
                    'is_staff': u['is_staff'],
                    'is_superuser': u['is_superuser'],
                }
            )
            user.set_password(u['password'])
            user.save()
            status = "Created" if created else "Updated password for"
            self.stdout.write(self.style.SUCCESS(f"  [✓] {status} {u['username']} (Role: {u['role']}) -> Pass: {u['password']}"))

        self.stdout.write(self.style.SUCCESS("\nDemonstration accounts ready!"))

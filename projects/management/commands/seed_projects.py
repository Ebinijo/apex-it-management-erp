from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from clients.models import Client
from employees.models import EmployeeProfile
from projects.models import Project

class Command(BaseCommand):
    help = 'Seeds initial engineering client projects and team assignments'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Client Software Projects..."))

        # Fetch Clients
        client_nexus = Client.objects.filter(client_id='CLT-001').first() or Client.objects.first()
        client_bio = Client.objects.filter(client_id='CLT-002').first() or Client.objects.first()
        client_omni = Client.objects.filter(client_id='CLT-003').first() or Client.objects.first()
        client_apex = Client.objects.filter(client_id='CLT-004').first() or Client.objects.first()

        # Fetch Project Manager
        pm = EmployeeProfile.objects.filter(user__username='pm_john').first() or EmployeeProfile.objects.first()

        # Fetch Developers
        dev_alex = EmployeeProfile.objects.filter(user__username='dev_alex').first()
        dev_priya = EmployeeProfile.objects.filter(user__username='dev_priya').first()
        qa_sam = EmployeeProfile.objects.filter(user__username='qa_sam').first()

        today = timezone.now().date()

        projects_data = [
            {
                'project_id': 'PRJ-001',
                'name': 'FinTech Core Banking API Engine',
                'client': client_nexus,
                'project_manager': pm,
                'start_date': today - timedelta(days=45),
                'deadline': today + timedelta(days=60),
                'status': Project.Status.IN_PROGRESS,
                'description': 'High-throughput payment orchestration and ledger transaction microservices engine with real-time audit verification.',
                'team': [dev_alex, dev_priya],
            },
            {
                'project_id': 'PRJ-002',
                'name': 'MediCare Telehealth WebRTC Platform',
                'client': client_bio,
                'project_manager': pm,
                'start_date': today - timedelta(days=30),
                'deadline': today + timedelta(days=25),
                'status': Project.Status.TESTING,
                'description': 'HIPAA-compliant video consultation platform with digital prescription signing and automated appointment scheduling.',
                'team': [dev_alex, qa_sam],
            },
            {
                'project_id': 'PRJ-003',
                'name': 'OmniCommerce Headless Storefront',
                'client': client_omni,
                'project_manager': pm,
                'start_date': today + timedelta(days=10),
                'deadline': today + timedelta(days=120),
                'status': Project.Status.PLANNING,
                'description': 'Next-generation headless e-commerce store with unified inventory sync, Algolia search integration, and multi-currency checkout.',
                'team': [dev_priya],
            },
            {
                'project_id': 'PRJ-004',
                'name': 'Autonomous Fleet Route Optimizer',
                'client': client_apex,
                'project_manager': pm,
                'start_date': today - timedelta(days=90),
                'deadline': today - timedelta(days=5),
                'status': Project.Status.COMPLETED,
                'description': 'GPS route optimization microservice utilizing Dijkstra heuristics to minimize diesel fuel consumption for commercial carrier fleets.',
                'team': [dev_alex, dev_priya, qa_sam],
            },
        ]

        for p_data in projects_data:
            team = p_data.pop('team', [])
            project, created = Project.objects.get_or_create(
                project_id=p_data['project_id'],
                defaults=p_data
            )
            if team:
                valid_team = [t for t in team if t is not None]
                project.team_members.set(valid_team)

            status_str = "Created" if created else "Found"
            self.stdout.write(self.style.SUCCESS(f"  [✓] {status_str} Project: {project.name} ({project.project_id}) [{project.get_status_display()}]"))

        self.stdout.write(self.style.SUCCESS("\nPhase 4 Engineering Projects seeding completed successfully!"))

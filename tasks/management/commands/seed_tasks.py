from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from projects.models import Project
from employees.models import EmployeeProfile
from accounts.models import User
from tasks.models import Task, Bug

class Command(BaseCommand):
    help = 'Seeds initial sprint tasks and reported bug defects across projects'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Sprint Tasks and Bug Issues..."))

        # Fetch Projects
        prj1 = Project.objects.filter(project_id='PRJ-001').first() or Project.objects.first()
        prj2 = Project.objects.filter(project_id='PRJ-002').first()
        prj3 = Project.objects.filter(project_id='PRJ-003').first()
        prj4 = Project.objects.filter(project_id='PRJ-004').first()

        # Fetch PM & Devs
        pm_user = User.objects.filter(username='pm_john').first()
        dev_alex = EmployeeProfile.objects.filter(user__username='dev_alex').first()
        dev_priya = EmployeeProfile.objects.filter(user__username='dev_priya').first()
        qa_sam = EmployeeProfile.objects.filter(user__username='qa_sam').first()

        today = timezone.now().date()

        # 1. Seed Tasks
        tasks_data = [
            # PRJ-001 Tasks (Core Banking) -> 2 completed, 1 in progress, 1 to-do = 50% progress!
            {
                'task_id': 'TSK-001',
                'title': 'Implement HMAC-SHA256 Webhook Verification',
                'project': prj1,
                'assigned_developer': dev_alex,
                'created_by': pm_user,
                'priority': Task.Priority.CRITICAL,
                'status': Task.Status.COMPLETED,
                'start_date': today - timedelta(days=20),
                'deadline': today - timedelta(days=5),
                'description': 'Cryptographically verify payment gateway incoming webhooks against replay attacks.',
            },
            {
                'task_id': 'TSK-002',
                'title': 'Design Database Migration for Transaction Partitioning',
                'project': prj1,
                'assigned_developer': dev_priya,
                'created_by': pm_user,
                'priority': Task.Priority.HIGH,
                'status': Task.Status.COMPLETED,
                'start_date': today - timedelta(days=15),
                'deadline': today - timedelta(days=2),
                'description': 'Partition raw ledger table by monthly intervals to accelerate query performance.',
            },
            {
                'task_id': 'TSK-003',
                'title': 'Build Redis Distributed Lock for Ledger Transfers',
                'project': prj1,
                'assigned_developer': dev_alex,
                'created_by': pm_user,
                'priority': Task.Priority.HIGH,
                'status': Task.Status.IN_PROGRESS,
                'start_date': today - timedelta(days=3),
                'deadline': today + timedelta(days=7),
                'description': 'Prevent double-spending during rapid concurrent balance withdrawal requests.',
            },
            {
                'task_id': 'TSK-004',
                'title': 'Setup Swagger OpenAPI Documentation Endpoints',
                'project': prj1,
                'assigned_developer': dev_priya,
                'created_by': pm_user,
                'priority': Task.Priority.MEDIUM,
                'status': Task.Status.TODO,
                'start_date': today,
                'deadline': today + timedelta(days=14),
                'description': 'Auto-generate interactive client swagger docs from Django view schemas.',
            },
            # PRJ-002 Tasks (MediCare Telehealth)
            {
                'task_id': 'TSK-005',
                'title': 'Implement WebRTC Signaling Handshake Server',
                'project': prj2,
                'assigned_developer': dev_alex,
                'created_by': pm_user,
                'priority': Task.Priority.CRITICAL,
                'status': Task.Status.COMPLETED,
                'start_date': today - timedelta(days=25),
                'deadline': today - timedelta(days=10),
                'description': 'Establish peer-to-peer audio/video connection using secure WebSocket signaling.',
            },
            {
                'task_id': 'TSK-006',
                'title': 'Automate Cross-Browser E2E Video Call Verification',
                'project': prj2,
                'assigned_developer': qa_sam,
                'created_by': pm_user,
                'priority': Task.Priority.HIGH,
                'status': Task.Status.IN_PROGRESS,
                'start_date': today - timedelta(days=5),
                'deadline': today + timedelta(days=10),
                'description': 'Cypress & Playwright suites for camera permission and call disconnect flows.',
            },
            # PRJ-003 Tasks (OmniCommerce Headless)
            {
                'task_id': 'TSK-007',
                'title': 'Algolia Search Engine Index Synchronization Worker',
                'project': prj3,
                'assigned_developer': dev_priya,
                'created_by': pm_user,
                'priority': Task.Priority.MEDIUM,
                'status': Task.Status.TODO,
                'start_date': today + timedelta(days=5),
                'deadline': today + timedelta(days=25),
                'description': 'Celery periodic task to sync inventory catalog changes to cloud Algolia indices.',
            },
            # PRJ-004 Tasks (Autonomous Fleet - Completed)
            {
                'task_id': 'TSK-008',
                'title': 'GPS Geofencing Polling & Telemetry Webhooks',
                'project': prj4,
                'assigned_developer': dev_alex,
                'created_by': pm_user,
                'priority': Task.Priority.HIGH,
                'status': Task.Status.COMPLETED,
                'start_date': today - timedelta(days=70),
                'deadline': today - timedelta(days=30),
                'description': 'Ingest raw GPS coordinates from long-haul trucks and dispatch geofence alerts.',
            },
        ]

        for t_data in tasks_data:
            if t_data['project']:
                task, created = Task.objects.get_or_create(
                    task_id=t_data['task_id'],
                    defaults=t_data
                )
                status_str = "Created" if created else "Found"
                self.stdout.write(self.style.SUCCESS(f"  [✓] {status_str} Task: {task.title} ({task.task_id}) [{task.get_status_display()}]"))

        # 2. Seed Bugs
        bugs_data = [
            {
                'bug_id': 'BUG-001',
                'title': 'NullPointerException when payment gateway response drops callback token',
                'project': prj1,
                'reported_by': dev_alex.user if dev_alex else pm_user,
                'assigned_developer': dev_alex,
                'priority': Bug.Priority.CRITICAL,
                'status': Bug.Status.IN_PROGRESS,
                'reported_date': today - timedelta(days=3),
                'description': 'When third-party bank sandbox returns HTTP 200 with an empty transaction token string, parsing crashes.',
                'resolution_notes': 'Reproduced in staging. Adding defensive validation for empty payload tokens.',
            },
            {
                'bug_id': 'BUG-002',
                'title': 'WebRTC audio stream muted on Safari iOS 17.4 mobile browser',
                'project': prj2,
                'reported_by': qa_sam.user if qa_sam else pm_user,
                'assigned_developer': dev_alex,
                'priority': Bug.Priority.HIGH,
                'status': Bug.Status.OPEN,
                'reported_date': today - timedelta(days=2),
                'description': 'Microphone permission prompt triggers, but audio track initializes with muted state until user toggles screen orientation.',
            },
            {
                'bug_id': 'BUG-003',
                'title': 'Algolia catalog price decimals display trailing zero artifacts',
                'project': prj3,
                'reported_by': dev_priya.user if dev_priya else pm_user,
                'assigned_developer': dev_priya,
                'priority': Bug.Priority.LOW,
                'status': Bug.Status.OPEN,
                'reported_date': today - timedelta(days=1),
                'description': 'Price of $19.99 shows as $19.99000001 due to IEEE 754 floating-point casting in JSON serializer.',
            },
            {
                'bug_id': 'BUG-004',
                'title': 'Dijkstra route solver memory spike during multi-stop optimization',
                'project': prj4,
                'reported_by': dev_alex.user if dev_alex else pm_user,
                'assigned_developer': dev_priya,
                'priority': Bug.Priority.HIGH,
                'status': Bug.Status.RESOLVED,
                'reported_date': today - timedelta(days=40),
                'description': 'Heap allocated for graph adjacency matrix was retaining visited node states after path solution.',
                'resolution_notes': 'Fixed by switching from recursive matrix search to iterative A* priority queue.',
            },
        ]

        for b_data in bugs_data:
            if b_data['project']:
                bug, created = Bug.objects.get_or_create(
                    bug_id=b_data['bug_id'],
                    defaults=b_data
                )
                status_str = "Created" if created else "Found"
                self.stdout.write(self.style.SUCCESS(f"  [✓] {status_str} Bug: {bug.title} ({bug.bug_id}) [{bug.get_status_display()}]"))

        self.stdout.write(self.style.SUCCESS("\nPhase 5 Tasks and Bug Tracking seeding completed successfully!"))

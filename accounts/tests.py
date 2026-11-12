from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User

class AccountsModelAndAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create users for all four enterprise roles
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='Password123!',
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True
        )
        self.hr_user = User.objects.create_user(
            username='hr_test',
            email='hr@test.com',
            password='Password123!',
            role=User.Role.HR
        )
        self.pm_user = User.objects.create_user(
            username='pm_test',
            email='pm@test.com',
            password='Password123!',
            role=User.Role.PROJECT_MANAGER
        )
        self.dev_user = User.objects.create_user(
            username='dev_test',
            email='dev@test.com',
            password='Password123!',
            role=User.Role.DEVELOPER
        )

    def test_user_model_role_properties(self):
        """Verify role helper properties on custom user model."""
        self.assertTrue(self.admin_user.is_admin_role)
        self.assertFalse(self.admin_user.is_dev_role)

        self.assertTrue(self.hr_user.is_hr_role)
        self.assertFalse(self.hr_user.is_pm_role)

        self.assertTrue(self.pm_user.is_pm_role)
        self.assertFalse(self.pm_user.is_admin_role)

        self.assertTrue(self.dev_user.is_dev_role)
        self.assertFalse(self.dev_user.is_hr_role)

    def test_login_valid_credentials(self):
        """Verify successful login redirect to dashboard."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'admin_test',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/', response.url)

    def test_login_invalid_credentials(self):
        """Verify login failure with incorrect password displays error."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'admin_test',
            'password': 'WrongPassword999'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")

    def test_role_based_access_control_forbidden_for_developer(self):
        """Developer role must NOT be permitted to access admin user management (403 Forbidden)."""
        self.client.login(username='dev_test', password='Password123!')
        response = self.client.get(reverse('accounts:user_list'))
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Access Denied", status_code=403)

    def test_role_based_access_control_allowed_for_admin(self):
        """Admin role can access user management successfully."""
        self.client.login(username='admin_test', password='Password123!')
        response = self.client.get(reverse('accounts:user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User Account Management")

    def test_logout_functionality(self):
        """Verify logout clears session and redirects to login."""
        self.client.login(username='dev_test', password='Password123!')
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_profile_update(self):
        """Authenticated user can update profile details."""
        self.client.login(username='dev_test', password='Password123!')
        response = self.client.post(reverse('accounts:profile'), {
            'first_name': 'Alex',
            'last_name': 'Updated',
            'email': 'alex.updated@company.com',
            'phone': '+1 555-987-6543',
            'designation': 'Senior Python Developer',
            'bio': 'Passionate about distributed backend architecture.'
        })
        self.assertEqual(response.status_code, 302)
        self.dev_user.refresh_from_db()
        self.assertEqual(self.dev_user.first_name, 'Alex')
        self.assertEqual(self.dev_user.email, 'alex.updated@company.com')
        self.assertEqual(self.dev_user.designation, 'Senior Python Developer')

    def test_admin_deactivate_user(self):
        """Admin can toggle user active status."""
        self.client.login(username='admin_test', password='Password123!')
        self.assertTrue(self.dev_user.is_active)
        response = self.client.get(reverse('accounts:user_toggle_status', kwargs={'pk': self.dev_user.pk}))
        self.assertEqual(response.status_code, 302)
        self.dev_user.refresh_from_db()
        self.assertFalse(self.dev_user.is_active)

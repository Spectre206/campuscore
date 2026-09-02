from django.test import TestCase
from django.urls import reverse

from accounts.models import User


class AuthenticationViewTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='adminpass', role=User.Role.ADMIN
        )
        self.teacher = User.objects.create_user(
            username='teacher', password='teacherpass', role=User.Role.TEACHER
        )
        self.student = User.objects.create_user(
            username='student', password='studentpass', role=User.Role.STUDENT
        )

    def test_login_redirects_to_home(self):
        response = self.client.post(
            reverse('login'), {'username': 'admin', 'password': 'adminpass'}
        )
        self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)

    def test_logout_requires_post(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 405)  # GET not allowed

        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def test_home_redirects_to_admin_dashboard_for_admin(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('admin-dashboard'))

    def test_role_based_dashboard_access(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('admin-dashboard'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('teacher-dashboard'))
        self.assertEqual(response.status_code, 403)

        self.client.login(username='teacher', password='teacherpass')
        response = self.client.get(reverse('teacher-dashboard'))
        self.assertEqual(response.status_code, 200)

        self.client.login(username='student', password='studentpass')
        response = self.client.get(reverse('admin-dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_redirects_to_login(self):
        response = self.client.get(reverse('admin-dashboard'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("admin-dashboard")}')

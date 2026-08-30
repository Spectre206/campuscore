from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User

class UserAPITest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='adminpass', role=User.Role.ADMIN)
        self.student = User.objects.create_user(username='student', password='studentpass', role=User.Role.STUDENT)

    def test_list_users_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/accounts/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_user_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'role': User.Role.STUDENT,
            'password': 'newpass123'
        }
        response = self.client.post('/accounts/api/users/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

    def test_list_users_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/accounts/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_access_returns_403(self):
        response = self.client.get('/accounts/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
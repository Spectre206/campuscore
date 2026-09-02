from rest_framework import status

from academics.models import Department
from academics.tests.base import BaseAPITestSetup


class DepartmentAPITest(BaseAPITestSetup):
    def test_list_departments_authenticated(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/v1/departments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_create_department_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {'name': 'Mathematics', 'code': 'MATH'}
        response = self.client.post('/api/v1/departments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Department.objects.count(), 2)

    def test_create_department_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        data = {'name': 'Mathematics', 'code': 'MATH'}
        response = self.client.post('/api/v1/departments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_access_returns_403(self):
        response = self.client.get('/api/v1/departments/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

from rest_framework.test import APITestCase
from rest_framework import status
from academics.models import Department

class DepartmentAPITest(APITestCase):
    def test_list_departments(self):
        Department.objects.create(name="Mathematics", code="MATH")
        response = self.client.get('/api/departments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_department(self):
        data = {'name': 'Physics', 'code': 'PHY'}
        response = self.client.post('/api/departments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Department.objects.count(), 1)
from rest_framework import status

from academics.models import Department
from academics.tests.base import BaseAPITestSetup


class DepartmentViewSetTest(BaseAPITestSetup):
    def setUp(self):
        super().setUp()
        # Additional departments for filtering/ordering tests
        Department.objects.create(name='Mathematics', code='MATH')
        Department.objects.create(name='Physics', code='PHY')

    def test_retrieve_department_as_authenticated(self):
        self.client.force_authenticate(user=self.student)
        dept = Department.objects.get(code='CS')
        response = self.client.get(f'/api/v1/departments/{dept.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'CS')

    def test_retrieve_department_unauthenticated_returns_403(self):
        dept = Department.objects.get(code='CS')
        response = self.client.get(f'/api/v1/departments/{dept.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_department_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        dept = Department.objects.get(code='CS')
        data = {'name': 'Computer Science Updated', 'code': 'CS'}
        response = self.client.put(f'/api/v1/departments/{dept.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dept.refresh_from_db()
        self.assertEqual(dept.name, 'Computer Science Updated')

    def test_partial_update_department_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        dept = Department.objects.get(code='CS')
        data = {'name': 'CS Department'}
        response = self.client.patch(f'/api/v1/departments/{dept.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dept.refresh_from_db()
        self.assertEqual(dept.name, 'CS Department')
        self.assertEqual(dept.code, 'CS')

    def test_update_department_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        dept = Department.objects.get(code='CS')
        data = {'name': 'Hacked', 'code': 'CS'}
        response = self.client.put(f'/api/v1/departments/{dept.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_department_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        dept = Department.objects.get(code='MATH')
        response = self.client.delete(f'/api/v1/departments/{dept.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Department.objects.filter(code='MATH').exists())

    def test_delete_department_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        dept = Department.objects.get(code='MATH')
        response = self.client.delete(f'/api/v1/departments/{dept.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_departments_by_code(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/v1/departments/?code=CS')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['code'], 'CS')

    def test_ordering_departments_by_name(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/v1/departments/?ordering=name')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [d['name'] for d in response.data['results']]
        self.assertEqual(names, sorted(names))

    def test_pagination_response_structure(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/v1/departments/?page=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

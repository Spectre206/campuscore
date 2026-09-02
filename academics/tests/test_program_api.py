from rest_framework import status

from academics.models import Program
from academics.tests.base import BaseAPITestSetup


class ProgramAPITest(BaseAPITestSetup):
    def test_list_programs_authenticated(self):
        Program.objects.create(name='BS CS', code='BSCS', department=self.dept)
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/v1/programs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['department_name'], 'Computer Science')

    def test_create_program_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {'name': 'BS Software Engineering', 'code': 'BSSE', 'department': self.dept.id}
        response = self.client.post('/api/v1/programs/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Program.objects.count(), 1)

    def test_create_program_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        data = {'name': 'BS Software Engineering', 'code': 'BSSE', 'department': self.dept.id}
        response = self.client.post('/api/v1/programs/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

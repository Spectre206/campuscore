from rest_framework import status

from academics.models import Section
from academics.tests.base import EnrollmentBaseSetup


class SectionAPITest(EnrollmentBaseSetup):
    def test_list_sections_authenticated(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/v1/sections/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_create_section_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            'name': 'Section B',
            'capacity': 25,
            'course': self.course.id,
            'teacher': self.teacher.id,
            'is_active': True,
        }
        response = self.client.post('/api/v1/sections/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Section.objects.count(), 2)

    def test_create_section_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        data = {
            'name': 'Section C',
            'capacity': 20,
            'course': self.course.id,
            'teacher': self.teacher.id,
            'is_active': True,
        }
        response = self.client.post('/api/v1/sections/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_section_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        data = {
            'name': 'Section D',
            'capacity': 20,
            'course': self.course.id,
            'teacher': self.teacher.id,
        }
        response = self.client.post('/api/v1/sections/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

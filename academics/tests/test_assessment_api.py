from rest_framework import status

from academics.models import Assessment
from academics.tests.base import EnrollmentBaseSetup
from accounts.models import User


class AssessmentAPITest(EnrollmentBaseSetup):
    def test_list_assessments_authenticated(self):
        Assessment.objects.create(
            section=self.section, name='Quiz', type='QUIZ', total_marks=10, date='2026-09-01'
        )
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/v1/assessments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_create_assessment_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        data = {
            'section': self.section.id,
            'name': 'Midterm',
            'type': 'EXAM',
            'total_marks': 50,
            'date': '2026-09-15',
        }
        response = self.client.post('/api/v1/assessments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Assessment.objects.count(), 1)

    def test_create_assessment_for_other_teacher_section_forbidden(self):
        other_teacher = User.objects.create_user(
            username='teacher2', password='pass', role=User.Role.TEACHER
        )
        self.client.force_authenticate(user=other_teacher)
        data = {
            'section': self.section.id,
            'name': 'Midterm',
            'type': 'EXAM',
            'total_marks': 50,
            'date': '2026-09-15',
        }
        response = self.client.post('/api/v1/assessments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_assessment_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        data = {
            'section': self.section.id,
            'name': 'Midterm',
            'type': 'EXAM',
            'total_marks': 50,
            'date': '2026-09-15',
        }
        response = self.client.post('/api/v1/assessments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

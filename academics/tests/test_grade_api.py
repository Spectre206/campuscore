from rest_framework import status

from academics.models import Assessment, Enrollment, Grade
from academics.tests.base import EnrollmentBaseSetup
from accounts.models import User
from notifications.models import Notification


class GradeAPITest(EnrollmentBaseSetup):
    def setUp(self):
        super().setUp()
        self.enrollment = Enrollment.objects.create(section=self.section, student=self.student)
        self.assessment = Assessment.objects.create(
            section=self.section, name='Midterm', type='EXAM', total_marks=50, date='2026-09-15'
        )

    def test_create_single_grade_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        data = {'assessment': self.assessment.id, 'enrollment': self.enrollment.id, 'marks': 45}
        response = self.client.post('/api/v1/grades/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Grade.objects.count(), 1)

    def test_create_bulk_grades_as_teacher(self):
        student2 = User.objects.create_user(
            username='student2', password='pass', role=User.Role.STUDENT
        )
        enrollment2 = Enrollment.objects.create(section=self.section, student=student2)
        data = [
            {'assessment': self.assessment.id, 'enrollment': self.enrollment.id, 'marks': 40},
            {'assessment': self.assessment.id, 'enrollment': enrollment2.id, 'marks': 35},
        ]
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post('/api/v1/grades/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Grade.objects.count(), 2)

    def test_marks_greater_than_total_rejected(self):
        self.client.force_authenticate(user=self.teacher)
        data = {'assessment': self.assessment.id, 'enrollment': self.enrollment.id, 'marks': 60}
        response = self.client.post('/api/v1/grades/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_grade_rejected(self):
        Grade.objects.create(assessment=self.assessment, enrollment=self.enrollment, marks=40)
        self.client.force_authenticate(user=self.teacher)
        data = {'assessment': self.assessment.id, 'enrollment': self.enrollment.id, 'marks': 30}
        response = self.client.post('/api/v1/grades/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_grade_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        data = {'assessment': self.assessment.id, 'enrollment': self.enrollment.id, 'marks': 40}
        response = self.client.post('/api/v1/grades/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_grade_creates_notification_for_student(self):
        self.client.force_authenticate(user=self.teacher)
        data = {'assessment': self.assessment.id, 'enrollment': self.enrollment.id, 'marks': 45}
        response = self.client.post('/api/v1/grades/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Notification.objects.filter(recipient=self.student).exists())

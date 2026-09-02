from rest_framework import status

from academics.models import Enrollment
from academics.tests.base import EnrollmentBaseSetup
from accounts.models import User
from notifications.models import Notification


class EnrollmentAPITest(EnrollmentBaseSetup):
    def test_list_enrollments_as_admin(self):
        Enrollment.objects.create(section=self.section, student=self.student)
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/v1/enrollments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_list_enrollments_as_student_shows_only_own(self):
        other_student = User.objects.create_user(
            username='other', password='pass', role=User.Role.STUDENT
        )
        Enrollment.objects.create(section=self.section, student=self.student)
        Enrollment.objects.create(section=self.section, student=other_student)
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/v1/enrollments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['student'], self.student.id)

    def test_create_enrollment_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {'section': self.section.id, 'student': self.student.id}
        response = self.client.post('/api/v1/enrollments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Enrollment.objects.count(), 1)

    def test_duplicate_enrollment_rejected(self):
        Enrollment.objects.create(section=self.section, student=self.student)
        self.client.force_authenticate(user=self.admin)
        data = {'section': self.section.id, 'student': self.student.id}
        response = self.client.post('/api/v1/enrollments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_capacity_exceeded_rejected(self):
        student2 = User.objects.create_user(
            username='student2', password='pass', role=User.Role.STUDENT
        )
        Enrollment.objects.create(section=self.section, student=self.student)
        Enrollment.objects.create(section=self.section, student=student2)
        student3 = User.objects.create_user(
            username='student3', password='pass', role=User.Role.STUDENT
        )
        self.client.force_authenticate(user=self.admin)
        data = {'section': self.section.id, 'student': student3.id}
        response = self.client.post('/api/v1/enrollments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_enrollment_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        data = {'section': self.section.id, 'student': self.student.id}
        response = self.client.post('/api/v1/enrollments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_enrollment_creates_notification_for_student(self):
        self.client.force_authenticate(user=self.admin)
        data = {'section': self.section.id, 'student': self.student.id}
        response = self.client.post('/api/v1/enrollments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Notification.objects.filter(recipient=self.student).exists())

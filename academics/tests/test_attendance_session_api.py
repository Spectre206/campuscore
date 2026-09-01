from rest_framework import status
from academics.tests.base import EnrollmentBaseSetup
from academics.models import AttendanceSession
from accounts.models import User

class AttendanceSessionAPITest(EnrollmentBaseSetup):
    def test_list_sessions_authenticated(self):
        AttendanceSession.objects.create(section=self.section, date='2026-08-30', created_by=self.teacher)
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/v1/attendance-sessions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    def test_create_session_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        data = {'section': self.section.id, 'date': '2026-08-30', 'title': 'Lecture 1', 'created_by': self.teacher.id}
        response = self.client.post('/api/v1/attendance-sessions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AttendanceSession.objects.count(), 1)

    def test_create_session_for_other_teacher_section_forbidden(self):
        other_teacher = User.objects.create_user(username='teacher2', password='pass', role=User.Role.TEACHER)
        self.client.force_authenticate(user=other_teacher)
        data = {'section': self.section.id, 'date': '2026-08-30', 'created_by': other_teacher.id}
        response = self.client.post('/api/v1/attendance-sessions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_session_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        data = {'section': self.section.id, 'date': '2026-08-30', 'created_by': self.teacher.id}
        response = self.client.post('/api/v1/attendance-sessions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
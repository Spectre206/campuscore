from rest_framework import status
from academics.tests.base import EnrollmentBaseSetup
from academics.models import AttendanceRecord, AttendanceSession, Enrollment, Section
from accounts.models import User

class AttendanceRecordAPITest(EnrollmentBaseSetup):
    def setUp(self):
        super().setUp()
        self.enrollment = Enrollment.objects.create(section=self.section, student=self.student)
        self.attendance_session = AttendanceSession.objects.create(section=self.section, date='2026-08-30', created_by=self.teacher)

    def test_create_single_record_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        data = {'session': self.attendance_session.id, 'enrollment': self.enrollment.id, 'status': 'PRESENT'}
        response = self.client.post('/api/v1/attendance-records/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AttendanceRecord.objects.count(), 1)

    def test_create_bulk_records_as_teacher(self):
        student2 = User.objects.create_user(username='student2', password='pass', role=User.Role.STUDENT)
        enrollment2 = Enrollment.objects.create(section=self.section, student=student2)
        data = [
            {'session': self.attendance_session.id, 'enrollment': self.enrollment.id, 'status': 'PRESENT'},
            {'session': self.attendance_session.id, 'enrollment': enrollment2.id, 'status': 'ABSENT'}
        ]
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post('/api/v1/attendance-records/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AttendanceRecord.objects.count(), 2)

    def test_create_record_for_wrong_section_enrollment(self):
        other_section = Section.objects.create(course=self.course, teacher=self.teacher, name="B")
        other_enrollment = Enrollment.objects.create(section=other_section, student=self.student)
        self.client.force_authenticate(user=self.teacher)
        data = {'session': self.attendance_session.id, 'enrollment': other_enrollment.id, 'status': 'PRESENT'}
        response = self.client.post('/api/v1/attendance-records/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_record_rejected(self):
        AttendanceRecord.objects.create(session=self.attendance_session, enrollment=self.enrollment, status=AttendanceRecord.Status.PRESENT)
        self.client.force_authenticate(user=self.teacher)
        data = {'session': self.attendance_session.id, 'enrollment': self.enrollment.id, 'status': 'ABSENT'}
        response = self.client.post('/api/v1/attendance-records/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_record_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        data = {'session': self.attendance_session.id, 'enrollment': self.enrollment.id, 'status': 'PRESENT'}
        response = self.client.post('/api/v1/attendance-records/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
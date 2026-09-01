from rest_framework import status
from academics.tests.base import EnrollmentBaseSetup
from academics.models import Assessment, Grade, Enrollment
from accounts.models import User

class GradeSummaryAPITest(EnrollmentBaseSetup):
    def setUp(self):
        super().setUp()
        self.enrollment = Enrollment.objects.create(section=self.section, student=self.student)
        self.assessment1 = Assessment.objects.create(section=self.section, name="Quiz", type="QUIZ", total_marks=10, date='2026-09-01')
        self.assessment2 = Assessment.objects.create(section=self.section, name="Midterm", type="EXAM", total_marks=50, date='2026-09-15')
        Grade.objects.create(assessment=self.assessment1, enrollment=self.enrollment, marks=8)
        Grade.objects.create(assessment=self.assessment2, enrollment=self.enrollment, marks=40)

    def test_student_can_view_own_grade_summary(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/v1/grade-summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        summary = response.data[0]
        self.assertEqual(summary['total_marks_obtained'], 48)
        self.assertEqual(summary['total_possible_marks'], 60)
        self.assertEqual(summary['percentage'], 80.0)

    def test_admin_can_view_student_summary_by_id(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f'/api/v1/grade-summary/?student_id={self.student.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_can_view_student_summary_by_id(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f'/api/v1/grade-summary/?student_id={self.student.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_cannot_view_other_student_summary(self):
        other_student = User.objects.create_user(username='other', password='pass', role=User.Role.STUDENT)
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/v1/grade-summary/?student_id={other_student.id}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_without_student_id_gets_400(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/v1/grade-summary/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
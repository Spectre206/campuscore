from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from academics.models import Department, Program, Course, Section, Enrollment, AttendanceSession, AttendanceRecord, Assessment, Grade

class BaseAPITestSetup(APITestCase):
    def setUp(self):
        # Create admin and student users
        self.admin = User.objects.create_user(
            username='admin',
            password='adminpass',
            role=User.Role.ADMIN
        )
        self.student = User.objects.create_user(
            username='student',
            password='studentpass',
            role=User.Role.STUDENT
        )
        self.dept = Department.objects.create(name="Computer Science", code="CS")

class DepartmentAPITest(BaseAPITestSetup):
    def test_list_departments_authenticated(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/departments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_department_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {'name': 'Mathematics', 'code': 'MATH'}
        response = self.client.post('/api/departments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Department.objects.count(), 2)

    def test_create_department_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        data = {'name': 'Mathematics', 'code': 'MATH'}
        response = self.client.post('/api/departments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_access_returns_403(self):
        response = self.client.get('/api/departments/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
class ProgramAPITest(BaseAPITestSetup):
    def setUp(self):
        super().setUp()
        self.program = Program.objects.create(
            name="BS Computer Science",
            code="BSCS",
            department=self.dept
        )

    def test_list_programs_authenticated(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/programs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['department_name'], "Computer Science")

    def test_create_program_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {'name': 'BS Software Engineering', 'code': 'BSSE', 'department': self.dept.id}
        response = self.client.post('/api/programs/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Program.objects.count(), 2)

    def test_create_program_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        data = {'name': 'BS Software Engineering', 'code': 'BSSE', 'department': self.dept.id}
        response = self.client.post('/api/programs/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class CourseAPITest(BaseAPITestSetup):
    def setUp(self):
        super().setUp()
        self.program = Program.objects.create(
            name="BS Computer Science",
            code="BSCS",
            department=self.dept
        )

    def test_list_courses_authenticated(self):
        Course.objects.create(name="Database Systems", code="DB101", program=self.program)
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['program_name'], "BS Computer Science")

    def test_create_course_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {'name': 'Data Structures', 'code': 'DS102', 'description': 'Core CS', 'program': self.program.id}
        response = self.client.post('/api/courses/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 1)

    def test_create_course_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        data = {'name': 'Data Structures', 'code': 'DS102', 'description': 'Core CS', 'program': self.program.id}
        response = self.client.post('/api/courses/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class EnrollmentBaseSetup(BaseAPITestSetup):
    def setUp(self):
        super().setUp()
        self.teacher = User.objects.create_user(
            username='teacher',
            password='teacherpass',
            role=User.Role.TEACHER
        )
        self.program = Program.objects.create(
            name="BS Computer Science",
            code="BSCS",
            department=self.dept
        )
        self.course = Course.objects.create(
            name="Database Systems",
            code="DB101",
            program=self.program
        )
        self.section = Section.objects.create(
            course=self.course,
            teacher=self.teacher,
            name="Section A",
            capacity=2  # small capacity for testing limit
        )

class SectionAPITest(EnrollmentBaseSetup):
    def test_list_sections_authenticated(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/sections/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_section_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            'name': 'Section B',
            'capacity': 25,
            'course': self.course.id,
            'teacher': self.teacher.id,
            'is_active': True
        }
        response = self.client.post('/api/sections/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Section.objects.count(), 2)

    def test_create_section_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        data = {
            'name': 'Section C',
            'capacity': 20,
            'course': self.course.id,
            'teacher': self.teacher.id,
            'is_active': True
        }
        response = self.client.post('/api/sections/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_section_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        data = {
            'name': 'Section D',
            'capacity': 20,
            'course': self.course.id,
            'teacher': self.teacher.id,
            'is_active': True
        }
        response = self.client.post('/api/sections/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class EnrollmentAPITest(EnrollmentBaseSetup):
    def test_list_enrollments_as_admin(self):
        Enrollment.objects.create(section=self.section, student=self.student)
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/enrollments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_enrollments_as_student_shows_only_own(self):
        other_student = User.objects.create_user(username='other', password='pass', role=User.Role.STUDENT)
        Enrollment.objects.create(section=self.section, student=self.student)
        Enrollment.objects.create(section=self.section, student=other_student)
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/enrollments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['student'], self.student.id)

    def test_create_enrollment_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            'section': self.section.id,
            'student': self.student.id,
            'status': 'ACTIVE'
        }
        response = self.client.post('/api/enrollments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Enrollment.objects.count(), 1)

    def test_duplicate_enrollment_rejected(self):
        Enrollment.objects.create(section=self.section, student=self.student)
        self.client.force_authenticate(user=self.admin)
        data = {
            'section': self.section.id,
            'student': self.student.id,
        }
        response = self.client.post('/api/enrollments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Optionally, assert that the error mentions uniqueness
        self.assertIn("unique", str(response.data).lower())

    def test_capacity_exceeded_rejected(self):
        # Fill capacity to 2
        student2 = User.objects.create_user(username='student2', password='pass', role=User.Role.STUDENT)
        Enrollment.objects.create(section=self.section, student=self.student)
        Enrollment.objects.create(section=self.section, student=student2)
        # Try to enroll a third student
        student3 = User.objects.create_user(username='student3', password='pass', role=User.Role.STUDENT)
        self.client.force_authenticate(user=self.admin)
        data = {
            'section': self.section.id,
            'student': student3.id,
        }
        response = self.client.post('/api/enrollments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("capacity exceeded", str(response.data))

    def test_create_enrollment_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        data = {
            'section': self.section.id,
            'student': self.student.id,
        }
        response = self.client.post('/api/enrollments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_enrollment_creates_notification_for_student(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            'section': self.section.id,
            'student': self.student.id,
        }
        response = self.client.post('/api/enrollments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check notification
        from notifications.models import Notification
        notif = Notification.objects.filter(recipient=self.student).first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.title, "Enrollment Successful")

class AttendanceSessionAPITest(EnrollmentBaseSetup):
    def test_list_sessions_authenticated(self):
        AttendanceSession.objects.create(section=self.section, date='2026-08-30', created_by=self.teacher)
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/attendance-sessions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_session_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        data = {
            'section': self.section.id,
            'date': '2026-08-30',
            'title': 'Lecture 1',
            'created_by': self.teacher.id
        }
        response = self.client.post('/api/attendance-sessions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AttendanceSession.objects.count(), 1)

    def test_create_session_for_other_teacher_section_forbidden(self):
        other_teacher = User.objects.create_user(username='teacher2', password='pass', role=User.Role.TEACHER)
        self.client.force_authenticate(user=other_teacher)
        data = {
            'section': self.section.id,
            'date': '2026-08-30',
            'title': 'Lecture',
            'created_by': other_teacher.id
        }
        response = self.client.post('/api/attendance-sessions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_session_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        data = {
            'section': self.section.id,
            'date': '2026-08-30',
            'created_by': self.teacher.id
        }
        response = self.client.post('/api/attendance-sessions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AttendanceRecordAPITest(EnrollmentBaseSetup):
    def setUp(self):
        super().setUp()
        self.enrollment = Enrollment.objects.create(section=self.section, student=self.student)
        self.attendance_session = AttendanceSession.objects.create(
            section=self.section,
            date='2026-08-30',
            created_by=self.teacher
        )

    def test_create_single_record_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        data = {
            'session': self.attendance_session.id,
            'enrollment': self.enrollment.id,
            'status': 'PRESENT'
        }
        response = self.client.post('/api/attendance-records/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AttendanceRecord.objects.count(), 1)

    def test_create_bulk_records_as_teacher(self):
        student2 = User.objects.create_user(username='student2', password='pass', role=User.Role.STUDENT)
        enrollment2 = Enrollment.objects.create(section=self.section, student=student2)
        self.client.force_authenticate(user=self.teacher)
        data = [
            {
                'session': self.attendance_session.id,
                'enrollment': self.enrollment.id,
                'status': 'PRESENT'
            },
            {
                'session': self.attendance_session.id,
                'enrollment': enrollment2.id,
                'status': 'ABSENT'
            }
        ]
        response = self.client.post('/api/attendance-records/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AttendanceRecord.objects.count(), 2)

    def test_create_record_for_wrong_section_enrollment(self):
        # Create another section and enrollment
        other_section = Section.objects.create(
            course=self.course,
            teacher=self.teacher,
            name="B"
        )
        other_enrollment = Enrollment.objects.create(section=other_section, student=self.student)
        self.client.force_authenticate(user=self.teacher)
        data = {
            'session': self.attendance_session.id,
            'enrollment': other_enrollment.id,
            'status': 'PRESENT'
        }
        response = self.client.post('/api/attendance-records/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_record_rejected(self):
        AttendanceRecord.objects.create(
            session=self.attendance_session,
            enrollment=self.enrollment,
            status=AttendanceRecord.Status.PRESENT
        )
        self.client.force_authenticate(user=self.teacher)
        data = {
            'session': self.attendance_session.id,
            'enrollment': self.enrollment.id,
            'status': 'ABSENT'
        }
        response = self.client.post('/api/attendance-records/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_record_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        data = {
            'session': self.attendance_session.id,
            'enrollment': self.enrollment.id,
            'status': 'PRESENT'
        }
        response = self.client.post('/api/attendance-records/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AttendanceSummaryAPITest(EnrollmentBaseSetup):
    def setUp(self):
        super().setUp()
        self.enrollment = Enrollment.objects.create(section=self.section, student=self.student)
        # Create two sessions and one present record
        self.session1 = AttendanceSession.objects.create(section=self.section, date='2026-08-30', created_by=self.teacher)
        self.session2 = AttendanceSession.objects.create(section=self.section, date='2026-08-31', created_by=self.teacher)
        AttendanceRecord.objects.create(session=self.session1, enrollment=self.enrollment, status=AttendanceRecord.Status.PRESENT)

    def test_student_can_view_own_summary(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/attendance-summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        summary = response.data[0]
        self.assertEqual(summary['total_sessions'], 2)
        self.assertEqual(summary['present'], 1)
        self.assertEqual(summary['percentage'], 50.0)

    def test_admin_can_view_student_summary_by_id(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f'/api/attendance-summary/?student_id={self.student.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_teacher_can_view_student_summary_by_id(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f'/api/attendance-summary/?student_id={self.student.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_student_cannot_view_other_student_summary(self):
        other_student = User.objects.create_user(username='other', password='pass', role=User.Role.STUDENT)
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/attendance-summary/?student_id={other_student.id}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_without_student_id_gets_400(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/attendance-summary/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class AssessmentAPITest(EnrollmentBaseSetup):
    def test_list_assessments_authenticated(self):
        Assessment.objects.create(
            section=self.section,
            name="Quiz 1",
            type="QUIZ",
            total_marks=10,
            date='2026-09-01'
        )
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/assessments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_assessment_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        data = {
            'section': self.section.id,
            'name': 'Midterm',
            'type': 'EXAM',
            'total_marks': 50,
            'date': '2026-09-15'
        }
        response = self.client.post('/api/assessments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Assessment.objects.count(), 1)

    def test_create_assessment_for_other_teacher_section_forbidden(self):
        other_teacher = User.objects.create_user(username='teacher2', password='pass', role=User.Role.TEACHER)
        self.client.force_authenticate(user=other_teacher)
        data = {
            'section': self.section.id,
            'name': 'Midterm',
            'type': 'EXAM',
            'total_marks': 50,
            'date': '2026-09-15'
        }
        response = self.client.post('/api/assessments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_assessment_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        data = {
            'section': self.section.id,
            'name': 'Midterm',
            'type': 'EXAM',
            'total_marks': 50,
            'date': '2026-09-15'
        }
        response = self.client.post('/api/assessments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GradeAPITest(EnrollmentBaseSetup):
    def setUp(self):
        super().setUp()
        self.enrollment = Enrollment.objects.create(section=self.section, student=self.student)
        self.assessment = Assessment.objects.create(
            section=self.section,
            name="Midterm",
            type="EXAM",
            total_marks=50,
            date='2026-09-15'
        )

    def test_create_single_grade_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        data = {
            'assessment': self.assessment.id,
            'enrollment': self.enrollment.id,
            'marks': 45
        }
        response = self.client.post('/api/grades/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Grade.objects.count(), 1)

    def test_create_bulk_grades_as_teacher(self):
        student2 = User.objects.create_user(username='student2', password='pass', role=User.Role.STUDENT)
        enrollment2 = Enrollment.objects.create(section=self.section, student=student2)
        self.client.force_authenticate(user=self.teacher)
        data = [
            {'assessment': self.assessment.id, 'enrollment': self.enrollment.id, 'marks': 40},
            {'assessment': self.assessment.id, 'enrollment': enrollment2.id, 'marks': 35}
        ]
        response = self.client.post('/api/grades/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Grade.objects.count(), 2)

    def test_marks_greater_than_total_rejected(self):
        self.client.force_authenticate(user=self.teacher)
        data = {
            'assessment': self.assessment.id,
            'enrollment': self.enrollment.id,
            'marks': 60  # > total_marks
        }
        response = self.client.post('/api/grades/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_grade_rejected(self):
        Grade.objects.create(assessment=self.assessment, enrollment=self.enrollment, marks=40)
        self.client.force_authenticate(user=self.teacher)
        data = {
            'assessment': self.assessment.id,
            'enrollment': self.enrollment.id,
            'marks': 30
        }
        response = self.client.post('/api/grades/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_grade_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        data = {
            'assessment': self.assessment.id,
            'enrollment': self.enrollment.id,
            'marks': 40
        }
        response = self.client.post('/api/grades/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_grade_creates_notification_for_student(self):
        self.client.force_authenticate(user=self.teacher)
        data = {
            'assessment': self.assessment.id,
            'enrollment': self.enrollment.id,
            'marks': 45
        }
        response = self.client.post('/api/grades/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check notification
        from notifications.models import Notification
        notif = Notification.objects.filter(recipient=self.student).first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.title, "Grade Posted")


class GradeSummaryAPITest(EnrollmentBaseSetup):
    def setUp(self):
        super().setUp()
        self.enrollment = Enrollment.objects.create(section=self.section, student=self.student)
        self.assessment1 = Assessment.objects.create(
            section=self.section,
            name="Quiz 1",
            type="QUIZ",
            total_marks=10,
            date='2026-09-01'
        )
        self.assessment2 = Assessment.objects.create(
            section=self.section,
            name="Midterm",
            type="EXAM",
            total_marks=50,
            date='2026-09-15'
        )
        Grade.objects.create(assessment=self.assessment1, enrollment=self.enrollment, marks=8)
        Grade.objects.create(assessment=self.assessment2, enrollment=self.enrollment, marks=40)

    def test_student_can_view_own_grade_summary(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/grade-summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        summary = response.data[0]
        self.assertEqual(summary['assessments_count'], 2)
        self.assertEqual(summary['total_marks_obtained'], 48)
        self.assertEqual(summary['total_possible_marks'], 60)
        self.assertEqual(summary['percentage'], 80.0)

    def test_admin_can_view_student_summary_by_id(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f'/api/grade-summary/?student_id={self.student.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_teacher_can_view_student_summary_by_id(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f'/api/grade-summary/?student_id={self.student.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_student_cannot_view_other_student_summary(self):
        other_student = User.objects.create_user(username='other', password='pass', role=User.Role.STUDENT)
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/grade-summary/?student_id={other_student.id}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_without_student_id_gets_400(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/grade-summary/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
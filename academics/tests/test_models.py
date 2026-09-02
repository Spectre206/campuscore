from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.db.utils import IntegrityError
from django.test import TestCase

from academics.models import (
    Assessment,
    AttendanceRecord,
    AttendanceSession,
    Course,
    Department,
    Enrollment,
    Grade,
    Program,
    Section,
)
from accounts.models import User


class DepartmentModelTest(TestCase):
    def test_create_department(self):
        dept = Department.objects.create(name='Computer Science', code='CS')
        self.assertEqual(dept.name, 'Computer Science')
        self.assertEqual(dept.code, 'CS')

    def test_code_unique(self):
        Department.objects.create(name='Computer Science', code='CS')
        with self.assertRaises(IntegrityError):
            Department.objects.create(name='Duplicate', code='CS')


class ProgramModelTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name='Computer Science', code='CS')

    def test_create_program(self):
        prog = Program.objects.create(name='BS Computer Science', code='BSCS', department=self.dept)
        self.assertEqual(prog.department, self.dept)
        self.assertIn(prog, self.dept.programs.all())

    def test_department_protect_on_delete(self):
        Program.objects.create(name='BS Computer Science', code='BSCS', department=self.dept)
        with self.assertRaises(ProtectedError):
            self.dept.delete()


class CourseModelTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name='Computer Science', code='CS')
        self.program = Program.objects.create(
            name='BS Computer Science', code='BSCS', department=self.dept
        )

    def test_create_course(self):
        course = Course.objects.create(name='Database Systems', code='DB101', program=self.program)
        self.assertEqual(course.program, self.program)
        self.assertIn(course, self.program.courses.all())

    def test_program_protect_on_delete(self):
        Course.objects.create(name='Database Systems', code='DB101', program=self.program)
        with self.assertRaises(ProtectedError):
            self.program.delete()


class SectionModelTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name='Computer Science', code='CS')
        self.program = Program.objects.create(name='BS CS', code='BSCS', department=self.dept)
        self.course = Course.objects.create(
            name='Database Systems', code='DB101', program=self.program
        )
        self.teacher = User.objects.create_user(
            username='teacher1', password='pass', role=User.Role.TEACHER
        )

    def test_create_section(self):
        section = Section.objects.create(
            course=self.course, teacher=self.teacher, name='Section A', capacity=30
        )
        self.assertEqual(section.course, self.course)
        self.assertEqual(section.teacher, self.teacher)

    def test_unique_together_course_name(self):
        Section.objects.create(course=self.course, teacher=self.teacher, name='Section A')
        with self.assertRaises(IntegrityError):
            Section.objects.create(course=self.course, teacher=self.teacher, name='Section A')


class EnrollmentModelTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name='CS', code='CS')
        self.program = Program.objects.create(name='BS CS', code='BSCS', department=self.dept)
        self.course = Course.objects.create(name='DB', code='DB101', program=self.program)
        self.teacher = User.objects.create_user(
            username='teacher1', password='pass', role=User.Role.TEACHER
        )
        self.student = User.objects.create_user(
            username='student1', password='pass', role=User.Role.STUDENT
        )
        self.section = Section.objects.create(
            course=self.course, teacher=self.teacher, name='A', capacity=10
        )

    def test_create_enrollment(self):
        enrollment = Enrollment.objects.create(section=self.section, student=self.student)
        self.assertEqual(enrollment.section, self.section)
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.status, Enrollment.Status.ACTIVE)

    def test_unique_together_section_student(self):
        Enrollment.objects.create(section=self.section, student=self.student)
        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(section=self.section, student=self.student)


class AttendanceSessionModelTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name='CS', code='CS')
        self.program = Program.objects.create(name='BSCS', code='BSCS', department=self.dept)
        self.course = Course.objects.create(name='DB', code='DB101', program=self.program)
        self.teacher = User.objects.create_user(
            username='teacher1', password='pass', role=User.Role.TEACHER
        )
        self.section = Section.objects.create(course=self.course, teacher=self.teacher, name='A')

    def test_create_session(self):
        session = AttendanceSession.objects.create(
            section=self.section, date='2026-08-30', title='Lecture 1', created_by=self.teacher
        )
        self.assertEqual(session.section, self.section)
        self.assertEqual(session.title, 'Lecture 1')


class AttendanceRecordModelTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name='CS', code='CS')
        self.program = Program.objects.create(name='BSCS', code='BSCS', department=self.dept)
        self.course = Course.objects.create(name='DB', code='DB101', program=self.program)
        self.teacher = User.objects.create_user(
            username='teacher1', password='pass', role=User.Role.TEACHER
        )
        self.student = User.objects.create_user(
            username='student1', password='pass', role=User.Role.STUDENT
        )
        self.section = Section.objects.create(course=self.course, teacher=self.teacher, name='A')
        self.enrollment = Enrollment.objects.create(section=self.section, student=self.student)
        self.session = AttendanceSession.objects.create(
            section=self.section, date='2026-08-30', created_by=self.teacher
        )

    def test_create_record(self):
        record = AttendanceRecord.objects.create(
            session=self.session, enrollment=self.enrollment, status=AttendanceRecord.Status.PRESENT
        )
        self.assertEqual(record.status, AttendanceRecord.Status.PRESENT)

    def test_unique_together_session_enrollment(self):
        AttendanceRecord.objects.create(session=self.session, enrollment=self.enrollment)
        with self.assertRaises(IntegrityError):
            AttendanceRecord.objects.create(session=self.session, enrollment=self.enrollment)


class AssessmentModelTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name='CS', code='CS')
        self.program = Program.objects.create(name='BSCS', code='BSCS', department=self.dept)
        self.course = Course.objects.create(name='DB', code='DB101', program=self.program)
        self.teacher = User.objects.create_user(
            username='teacher1', password='pass', role=User.Role.TEACHER
        )
        self.section = Section.objects.create(course=self.course, teacher=self.teacher, name='A')

    def test_create_assessment(self):
        assessment = Assessment.objects.create(
            section=self.section,
            name='Midterm',
            type=Assessment.Type.EXAM,
            total_marks=50,
            date='2026-09-15',
        )
        self.assertEqual(assessment.total_marks, 50)

    def test_type_choices(self):
        assessment = Assessment.objects.create(
            section=self.section, name='Quiz 1', type='QUIZ', total_marks=10, date='2026-09-01'
        )
        self.assertEqual(assessment.type, 'QUIZ')


class GradeModelTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name='CS', code='CS')
        self.program = Program.objects.create(name='BSCS', code='BSCS', department=self.dept)
        self.course = Course.objects.create(name='DB', code='DB101', program=self.program)
        self.teacher = User.objects.create_user(
            username='teacher1', password='pass', role=User.Role.TEACHER
        )
        self.student = User.objects.create_user(
            username='student1', password='pass', role=User.Role.STUDENT
        )
        self.section = Section.objects.create(course=self.course, teacher=self.teacher, name='A')
        self.enrollment = Enrollment.objects.create(section=self.section, student=self.student)
        self.assessment = Assessment.objects.create(
            section=self.section, name='Midterm', type='EXAM', total_marks=50, date='2026-09-15'
        )

    def test_create_grade(self):
        grade = Grade.objects.create(
            assessment=self.assessment, enrollment=self.enrollment, marks=45
        )
        self.assertEqual(grade.marks, 45)

    def test_marks_non_negative_db_constraint(self):
        with self.assertRaises(IntegrityError):
            Grade.objects.create(assessment=self.assessment, enrollment=self.enrollment, marks=-5)

    def test_marks_cannot_exceed_total_marks_via_clean(self):
        grade = Grade(
            assessment=self.assessment,
            enrollment=self.enrollment,
            marks=60,  # > total_marks
        )
        with self.assertRaises(ValidationError):
            grade.full_clean()  # calls clean() and checks constraints

    def test_unique_together_assessment_enrollment(self):
        Grade.objects.create(assessment=self.assessment, enrollment=self.enrollment, marks=40)
        with self.assertRaises(IntegrityError):
            Grade.objects.create(assessment=self.assessment, enrollment=self.enrollment, marks=30)

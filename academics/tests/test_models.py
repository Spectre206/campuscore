from django.db import transaction
from django.db.models.deletion import ProtectedError
from academics.models import Department, Program, Course, Section, Enrollment
from accounts.models import User
from django.test import TestCase
from django.db.utils import IntegrityError

class DepartmentModelTest(TestCase):
    def test_create_department(self):
        dept = Department.objects.create(name="Computer Science", code="CS")
        self.assertEqual(dept.name, "Computer Science")
        self.assertEqual(dept.code, "CS")

    def test_code_unique(self):
        Department.objects.create(name="Computer Science", code="CS")
        with self.assertRaises(IntegrityError):
            Department.objects.create(name="Duplicate", code="CS")

class ProgramModelTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name="Computer Science", code="CS")

    def test_create_program(self):
        prog = Program.objects.create(
            name="BS Computer Science",
            code="BSCS",
            department=self.dept
        )
        self.assertEqual(prog.department, self.dept)
        self.assertIn(prog, self.dept.programs.all())

    def test_department_protect_on_delete(self):
        Program.objects.create(
            name="BS Computer Science",
            code="BSCS",
            department=self.dept
        )
        with self.assertRaises(ProtectedError):
            self.dept.delete()

class CourseModelTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name="Computer Science", code="CS")
        self.program = Program.objects.create(
            name="BS Computer Science",
            code="BSCS",
            department=self.dept
        )

    def test_create_course(self):
        course = Course.objects.create(
            name="Database Systems",
            code="DB101",
            program=self.program
        )
        self.assertEqual(course.program, self.program)
        self.assertIn(course, self.program.courses.all())

    def test_program_protect_on_delete(self):
        Course.objects.create(
            name="Database Systems",
            code="DB101",
            program=self.program
        )
        with self.assertRaises(ProtectedError):
            self.program.delete()

class SectionModelTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name="Computer Science", code="CS")
        self.program = Program.objects.create(name="BS CS", code="BSCS", department=self.dept)
        self.course = Course.objects.create(name="Database Systems", code="DB101", program=self.program)
        self.teacher = User.objects.create_user(username='teacher1', password='pass', role=User.Role.TEACHER)

    def test_create_section(self):
        section = Section.objects.create(course=self.course, teacher=self.teacher, name="Section A", capacity=30)
        self.assertEqual(section.course, self.course)
        self.assertEqual(section.teacher, self.teacher)

    def test_unique_together_course_name(self):
        Section.objects.create(course=self.course, teacher=self.teacher, name="Section A")
        with self.assertRaises(IntegrityError):
            Section.objects.create(course=self.course, teacher=self.teacher, name="Section A")


class EnrollmentModelTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name="CS", code="CS")
        self.program = Program.objects.create(name="BS CS", code="BSCS", department=self.dept)
        self.course = Course.objects.create(name="DB", code="DB101", program=self.program)
        self.teacher = User.objects.create_user(username='teacher1', password='pass', role=User.Role.TEACHER)
        self.student = User.objects.create_user(username='student1', password='pass', role=User.Role.STUDENT)
        self.section = Section.objects.create(course=self.course, teacher=self.teacher, name="A", capacity=10)

    def test_create_enrollment(self):
        enrollment = Enrollment.objects.create(section=self.section, student=self.student)
        self.assertEqual(enrollment.section, self.section)
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.status, Enrollment.Status.ACTIVE)

    def test_unique_together_section_student(self):
        Enrollment.objects.create(section=self.section, student=self.student)
        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(section=self.section, student=self.student)
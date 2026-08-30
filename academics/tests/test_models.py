from django.test import TestCase
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from academics.models import Department, Program, Course

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
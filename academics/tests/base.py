# academics/tests/base.py
from rest_framework.test import APITestCase

from academics.models import Course, Department, Program, Section
from accounts.models import User


class BaseAPITestSetup(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='adminpass', role=User.Role.ADMIN
        )
        self.student = User.objects.create_user(
            username='student', password='studentpass', role=User.Role.STUDENT
        )
        self.dept = Department.objects.create(name='Computer Science', code='CS')


class EnrollmentBaseSetup(BaseAPITestSetup):
    def setUp(self):
        super().setUp()
        self.teacher = User.objects.create_user(
            username='teacher', password='teacherpass', role=User.Role.TEACHER
        )
        self.program = Program.objects.create(
            name='BS Computer Science', code='BSCS', department=self.dept
        )
        self.course = Course.objects.create(
            name='Database Systems', code='DB101', program=self.program
        )
        self.section = Section.objects.create(
            course=self.course, teacher=self.teacher, name='Section A', capacity=2
        )

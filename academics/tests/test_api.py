from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from academics.models import Department, Program, Course

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
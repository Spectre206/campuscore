from rest_framework.test import APITestCase
from rest_framework import status
from academics.models import Department, Program, Course

class DepartmentAPITest(APITestCase):
    def test_list_departments(self):
        Department.objects.create(name="Mathematics", code="MATH")
        response = self.client.get('/api/departments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_department(self):
        data = {'name': 'Physics', 'code': 'PHY'}
        response = self.client.post('/api/departments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Department.objects.count(), 1)

class ProgramAPITest(APITestCase):
    def setUp(self):
        self.dept = Department.objects.create(name="Computer Science", code="CS")

    def test_list_programs(self):
        Program.objects.create(name="BS Computer Science", code="BSCS", department=self.dept)
        response = self.client.get('/api/programs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['department_name'], "Computer Science")

    def test_create_program(self):
        data = {
            'name': 'BS Software Engineering',
            'code': 'BSSE',
            'department': self.dept.id
        }
        response = self.client.post('/api/programs/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Program.objects.count(), 1)


class CourseAPITest(APITestCase):
    def setUp(self):
        self.dept = Department.objects.create(name="Computer Science", code="CS")
        self.program = Program.objects.create(
            name="BS Computer Science",
            code="BSCS",
            department=self.dept
        )

    def test_list_courses(self):
        Course.objects.create(name="Database Systems", code="DB101", program=self.program)
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['program_name'], "BS Computer Science")

    def test_create_course(self):
        data = {
            'name': 'Data Structures',
            'code': 'DS102',
            'description': 'Core CS course',
            'program': self.program.id
        }
        response = self.client.post('/api/courses/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 1)
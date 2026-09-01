from rest_framework import status
from academics.tests.base import BaseAPITestSetup
from academics.models import Program, Course

class CourseAPITest(BaseAPITestSetup):
    def setUp(self):
        super().setUp()
        self.program = Program.objects.create(name="BS CS", code="BSCS", department=self.dept)

    def test_list_courses_authenticated(self):
        Course.objects.create(name="DB", code="DB101", program=self.program)
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/v1/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['program_name'], "BS CS")    
    def test_create_course_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {'name': 'Data Structures', 'code': 'DS102', 'description': 'Core CS', 'program': self.program.id}
        response = self.client.post('/api/v1/courses/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 1)

    def test_create_course_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student)
        data = {'name': 'Data Structures', 'code': 'DS102', 'program': self.program.id}
        response = self.client.post('/api/v1/courses/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
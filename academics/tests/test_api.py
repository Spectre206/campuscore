from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from academics.models import Department, Program, Course, Section, Enrollment

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
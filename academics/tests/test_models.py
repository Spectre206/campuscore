from django.test import TestCase
from django.db import IntegrityError
from academics.models import Department

class DepartmentModelTest(TestCase):
    def test_create_department(self):
        dept = Department.objects.create(name="Computer Science", code="CS")
        self.assertEqual(dept.name, "Computer Science")
        self.assertEqual(dept.code, "CS")

    def test_code_unique(self):
        Department.objects.create(name="Computer Science", code="CS")
        with self.assertRaises(IntegrityError):
            Department.objects.create(name="Duplicate", code="CS")
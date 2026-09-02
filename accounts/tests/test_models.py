from django.test import TestCase

from accounts.models import User


class UserModelTest(TestCase):
    def test_default_role_is_student(self):
        user = User.objects.create_user(username='testuser', password='pass123')
        self.assertEqual(user.role, User.Role.STUDENT)

    def test_role_choices(self):
        user = User.objects.create_user(
            username='adminuser', password='pass123', role=User.Role.ADMIN
        )
        self.assertEqual(user.role, User.Role.ADMIN)

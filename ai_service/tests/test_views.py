from django.test import TestCase
from django.urls import reverse

from accounts.models import User


class QuizGeneratorViewTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher', password='pass123', role=User.Role.TEACHER
        )
        self.student = User.objects.create_user(
            username='student', password='pass123', role=User.Role.STUDENT
        )

    def test_teacher_can_access_page(self):
        self.client.login(username='teacher', password='pass123')
        response = self.client.get(reverse('ai-quiz-generator'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Quiz Generator')

    def test_student_forbidden(self):
        self.client.login(username='student', password='pass123')
        response = self.client.get(reverse('ai-quiz-generator'))
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_redirected(self):
        response = self.client.get(reverse('ai-quiz-generator'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("ai-quiz-generator")}')

    def test_teacher_post_generates_questions(self):
        self.client.login(username='teacher', password='pass123')
        response = self.client.post(
            reverse('ai-quiz-generator'),
            {'topic': 'Database', 'num_questions': '3'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Generated Questions')
        self.assertContains(response, 'Sample question 1')

    def test_teacher_post_invalid_form(self):
        self.client.login(username='teacher', password='pass123')
        response = self.client.post(
            reverse('ai-quiz-generator'),
            {'topic': '', 'num_questions': '3'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')

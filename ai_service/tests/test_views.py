from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import User


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_STORE_EAGER_RESULT=True,
)
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

    def test_teacher_post_generates_loading_state(self):
        self.client.login(username='teacher', password='pass123')
        response = self.client.post(
            reverse('ai-quiz-generator'),
            {'topic': 'Database', 'num_questions': '3'},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Generating questions...')

    def test_teacher_post_invalid_form(self):
        self.client.login(username='teacher', password='pass123')
        response = self.client.post(
            reverse('ai-quiz-generator'),
            {'topic': '', 'num_questions': '3'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')

    @patch('ai_service.views.AsyncResult')
    def test_quiz_result_partial_returns_questions_when_ready(self, mock_async_result):
        fake_result = MagicMock()
        fake_result.ready.return_value = True
        fake_result.successful.return_value = True
        fake_result.result = [{'question': 'Sample question 1'}]
        mock_async_result.return_value = fake_result

        self.client.login(username='teacher', password='pass123')
        session = self.client.session
        session['quiz_task_id'] = 'fake-task-id'
        session.save()

        response = self.client.get(reverse('quiz-result-partial'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Generated Questions')
        self.assertContains(response, 'Sample question 1')

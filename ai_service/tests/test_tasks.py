from unittest.mock import patch

from django.test import TestCase, override_settings

from ai_service.tasks import generate_quiz_questions_task


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class AIServiceTaskTest(TestCase):
    @patch('ai_service.tasks.generate_quiz_questions')
    def test_task_returns_questions(self, mock_generate):
        mock_generate.return_value = [{'question': 'Q?'}]
        result = generate_quiz_questions_task.delay('mock', 'Topic', 1)
        self.assertTrue(result.successful())
        self.assertEqual(result.result[0]['question'], 'Q?')
        mock_generate.assert_called_once_with('mock', 'Topic', 1)

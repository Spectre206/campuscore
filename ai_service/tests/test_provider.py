from django.test import SimpleTestCase

from ai_service.providers.base import AIProvider
from ai_service.providers.mock import MockAIProvider
from ai_service.service import generate_quiz_questions, get_provider


class MockAIProviderTest(SimpleTestCase):
    def setUp(self):
        self.provider = MockAIProvider()

    def test_generate_quiz_questions_returns_list(self):
        questions = self.provider.generate_quiz_questions('Database', 3)
        self.assertIsInstance(questions, list)
        self.assertEqual(len(questions), 3)

    def test_question_format(self):
        questions = self.provider.generate_quiz_questions('Database', 1)
        q = questions[0]
        self.assertIn('type', q)
        self.assertIn('question', q)
        self.assertIn('options', q)
        self.assertIn('answer', q)
        self.assertEqual(q['type'], 'multiple_choice')

    def test_service_get_provider(self):
        provider = get_provider('mock')
        self.assertIsInstance(provider, AIProvider)

    def test_service_get_unknown_provider_raises(self):
        with self.assertRaises(ValueError):
            get_provider('unknown')

    def test_generate_quiz_questions_service(self):
        questions = generate_quiz_questions('mock', 'Topic', 5)
        self.assertEqual(len(questions), 5)

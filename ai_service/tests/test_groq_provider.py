from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from ai_service.providers.groq import GroqAIProvider


class GroqAIProviderTest(SimpleTestCase):
    @patch('ai_service.providers.groq.Groq')
    def test_generate_quiz_questions_success(self, mock_groq_class):
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='[{"type":"multiple_choice","question":"Q?","options":["A","B","C","D"],"answer":"A"}]'
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response

        provider = GroqAIProvider()
        questions = provider.generate_quiz_questions('Test', 1)
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0]['question'], 'Q?')

    @patch('ai_service.providers.groq.Groq')
    def test_generate_quiz_questions_parses_markdown(self, mock_groq_class):
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client
        content = (
            '```json\n[{"type":"multiple_choice","question":"Q?",'
            '"options":["A","B","C","D"],"answer":"A"}]\n```'
        )
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=content))]
        mock_client.chat.completions.create.return_value = mock_response

        provider = GroqAIProvider()
        questions = provider.generate_quiz_questions('Test', 1)
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0]['answer'], 'A')

    @patch('ai_service.providers.groq.Groq')
    def test_generate_quiz_questions_invalid_response_raises(self, mock_groq_class):
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='No JSON here'))]
        mock_client.chat.completions.create.return_value = mock_response

        provider = GroqAIProvider()
        with self.assertRaises(ValueError):
            provider.generate_quiz_questions('Test', 1)

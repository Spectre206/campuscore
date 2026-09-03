from .base import AIProvider


class MockAIProvider(AIProvider):
    def generate_quiz_questions(self, topic, num_questions):
        questions = []
        for i in range(num_questions):
            questions.append(
                {
                    'type': 'multiple_choice',
                    'question': f'Sample question {i + 1} about {topic}?',
                    'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                    'answer': 'Option A',
                }
            )
        return questions

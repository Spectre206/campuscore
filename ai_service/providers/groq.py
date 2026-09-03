import json
import os
import re

from groq import Groq

from .base import AIProvider


class GroqAIProvider(AIProvider):
    def __init__(self):
        api_key = os.environ.get('GROQ_API_KEY')
        if not api_key:
            raise ValueError('GROQ_API_KEY environment variable is not set.')
        self.client = Groq(api_key=api_key)
        self.model = os.environ.get('GROQ_MODEL', 'groq/compound')

    def generate_quiz_questions(self, topic, num_questions):
        prompt = (
            f"Generate {num_questions} multiple-choice quiz questions about '{topic}'. "
            "Return ONLY a JSON array. Each object must have keys: 'type', 'question', "
            "'options' (array of 4 strings), and 'answer' (one of the options). "
            'Do not include any extra text.'
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {'role': 'system', 'content': 'You are an expert quiz generator.'},
                {'role': 'user', 'content': prompt},
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        content = response.choices[0].message.content.strip()

        # Use regex to extract the JSON array (handles markdown fences and extra text)
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            content = match.group(0)
        else:
            raise ValueError(f'No JSON array found in AI response: {content[:200]}')

        questions = json.loads(content)
        return questions

from .providers.base import AIProvider
from .providers.groq import GroqAIProvider
from .providers.mock import MockAIProvider

PROVIDERS = {
    'mock': MockAIProvider,
    'groq': GroqAIProvider,
}


def get_provider(name: str) -> AIProvider:
    provider_class = PROVIDERS.get(name)
    if not provider_class:
        raise ValueError(f'Unknown provider: {name}')
    return provider_class()


def generate_quiz_questions(provider_name: str, topic: str, num_questions: int) -> list[dict]:
    try:
        provider = get_provider(provider_name)
        return provider.generate_quiz_questions(topic, num_questions)
    except Exception as e:
        # Fallback to mock provider on any failure
        print(f'AI provider error: {e}. Falling back to mock.')
        return MockAIProvider().generate_quiz_questions(topic, num_questions)

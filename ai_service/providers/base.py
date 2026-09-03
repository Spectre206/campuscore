from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    def generate_quiz_questions(self, topic: str, num_questions: int) -> list[dict]:
        """Generate quiz questions as list of dicts with keys: type, question, options, answer."""
        pass

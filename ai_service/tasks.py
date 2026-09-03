from celery import shared_task

from .service import generate_quiz_questions


@shared_task
def generate_quiz_questions_task(provider_name, topic, num_questions):
    return generate_quiz_questions(provider_name, topic, num_questions)

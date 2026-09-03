from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from accounts.decorators import role_required
from accounts.models import User

from .forms import QuizGenerationForm
from .service import generate_quiz_questions


@login_required
@role_required([User.Role.TEACHER, User.Role.ADMIN])
def generate_quiz_view(request):
    questions = None
    form = QuizGenerationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        topic = form.cleaned_data['topic']
        num_questions = int(form.cleaned_data['num_questions'])
        try:
            questions = generate_quiz_questions('mock', topic, num_questions)
        except Exception as e:
            form.add_error(None, f'AI service error: {e}')

    return render(
        request,
        'ai_service/quiz_generator.html',
        {'form': form, 'questions': questions},
    )
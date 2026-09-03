import os

from celery.result import AsyncResult
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from accounts.decorators import role_required
from accounts.models import User

from .forms import QuizGenerationForm
from .tasks import generate_quiz_questions_task


@login_required
@role_required([User.Role.TEACHER, User.Role.ADMIN])
def generate_quiz_view(request):
    questions = None
    task_id = request.session.get('quiz_task_id')
    form = QuizGenerationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        topic = form.cleaned_data['topic']
        num_questions = int(form.cleaned_data['num_questions'])
        provider_name = os.environ.get('AI_PROVIDER', 'mock')
        task = generate_quiz_questions_task.delay(provider_name, topic, num_questions)
        request.session['quiz_task_id'] = task.id
        return redirect('ai-quiz-generator')  # to clear POST

    if task_id:
        result = AsyncResult(task_id)
        if result.ready():
            if result.successful():
                questions = result.result
                request.session.pop('quiz_task_id', None)
            else:
                form.add_error(None, 'AI generation failed.')
                request.session.pop('quiz_task_id', None)

    return render(
        request,
        'ai_service/quiz_generator.html',
        {
            'form': form,
            'questions': questions,
            'task_id': task_id,
        },
    )


@login_required
def quiz_task_status(request, task_id):
    result = AsyncResult(task_id)
    response_data = {
        'ready': result.ready(),
        'successful': result.successful() if result.ready() else None,
        'questions': result.result if result.ready() and result.successful() else None,
    }
    return JsonResponse(response_data)


@login_required
def quiz_result_partial(request):
    task_id = request.session.get('quiz_task_id')
    if not task_id:
        return HttpResponse('')

    result = AsyncResult(task_id)
    if result.ready() and result.successful():
        questions = result.result
        request.session.pop('quiz_task_id', None)
        return render(request, 'ai_service/partials/quiz_questions.html', {'questions': questions})
    else:
        # Still pending: return the polling element again
        return render(request, 'ai_service/partials/loading_spinner_polling.html')

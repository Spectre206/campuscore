from django.urls import path

from . import views

urlpatterns = [
    path('quiz-generator/', views.generate_quiz_view, name='ai-quiz-generator'),
    path('quiz-task/<task_id>/', views.quiz_task_status, name='quiz-task-status'),
    path('quiz-result-partial/', views.quiz_result_partial, name='quiz-result-partial'),
]

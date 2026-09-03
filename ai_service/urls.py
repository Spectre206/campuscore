from django.urls import path
from . import views

urlpatterns = [
    path('quiz-generator/', views.generate_quiz_view, name='ai-quiz-generator'),
]
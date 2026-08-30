from django.urls import path
from . import views
from .api_views import (
    DepartmentListCreateAPIView,
    ProgramListCreateAPIView,
    CourseListCreateAPIView,
)

urlpatterns = [
    path('departments/', views.department_list, name='department-list'),
    path('api/departments/', DepartmentListCreateAPIView.as_view(), name='api-department-list'),
    path('api/programs/', ProgramListCreateAPIView.as_view(), name='api-program-list'),
    path('api/courses/', CourseListCreateAPIView.as_view(), name='api-course-list'),
]
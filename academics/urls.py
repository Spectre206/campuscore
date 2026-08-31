from django.urls import path
from . import views
from .api_views import (
    DepartmentListCreateAPIView,
    ProgramListCreateAPIView,
    CourseListCreateAPIView,
    SectionListCreateAPIView,
    EnrollmentListCreateAPIView,
    AttendanceSessionListCreateAPIView,
    AttendanceRecordListCreateAPIView,
    AttendanceSummaryAPIView,
    AssessmentListCreateAPIView,
    GradeListCreateAPIView,
    GradeSummaryAPIView
)

urlpatterns = [
    path('departments/', views.department_list, name='department-list'),
    path('api/departments/', DepartmentListCreateAPIView.as_view(), name='api-department-list'),
    path('api/programs/', ProgramListCreateAPIView.as_view(), name='api-program-list'),
    path('api/courses/', CourseListCreateAPIView.as_view(), name='api-course-list'),
    path('api/sections/', SectionListCreateAPIView.as_view(), name='api-section-list'),
    path('api/enrollments/', EnrollmentListCreateAPIView.as_view(), name='api-enrollment-list'),
    path('api/attendance-sessions/', AttendanceSessionListCreateAPIView.as_view(), name='api-attendance-session-list'),
    path('api/attendance-records/', AttendanceRecordListCreateAPIView.as_view(), name='api-attendance-record-list'),
    path('api/attendance-summary/', AttendanceSummaryAPIView.as_view(), name='api-attendance-summary'),
    path('api/assessments/', AssessmentListCreateAPIView.as_view(), name='api-assessment-list'),
    path('api/grades/', GradeListCreateAPIView.as_view(), name='api-grade-list'),
    path('api/grade-summary/', GradeSummaryAPIView.as_view(), name='api-grade-summary')
]
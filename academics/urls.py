# academics/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .api_views import (
    AssessmentViewSet,
    AttendanceRecordViewSet,
    AttendanceSessionViewSet,
    AttendanceSummaryAPIView,
    CourseViewSet,
    DepartmentViewSet,
    EnrollmentViewSet,
    GradeSummaryAPIView,
    GradeViewSet,
    ProgramViewSet,
    SectionViewSet,
)

router = DefaultRouter()
router.register(r'api/v1/departments', DepartmentViewSet, basename='department')
router.register(r'api/v1/programs', ProgramViewSet, basename='program')
router.register(r'api/v1/courses', CourseViewSet, basename='course')
router.register(r'api/v1/sections', SectionViewSet, basename='section')
router.register(r'api/v1/enrollments', EnrollmentViewSet, basename='enrollment')
router.register(
    r'api/v1/attendance-sessions', AttendanceSessionViewSet, basename='attendance-session'
)
router.register(r'api/v1/attendance-records', AttendanceRecordViewSet, basename='attendance-record')
router.register(r'api/v1/assessments', AssessmentViewSet, basename='assessment')
router.register(r'api/v1/grades', GradeViewSet, basename='grade')

urlpatterns = [
    # Web views
    path('departments/', views.department_list, name='department-list'),
    path('my-sections/', views.teacher_section_list, name='teacher-section-list'),
    path('my-enrollments/', views.student_enrollment_list, name='student-enrollment-list'),
    path(
        'sections/<int:section_id>/attendance/',
        views.section_attendance_sessions,
        name='section-attendance-session-list',
    ),
    path(
        'sections/<int:section_id>/attendance/create/',
        views.attendance_session_create,
        name='section-attendance-session-create',
    ),
    path(
        'attendance-sessions/<int:session_id>/mark/', views.attendance_mark, name='attendance-mark'
    ),
    path('my-attendance/', views.student_attendance_summary, name='student-attendance-summary'),
    # Custom API endpoints (non-ViewSet)
    path(
        'api/v1/attendance-summary/',
        AttendanceSummaryAPIView.as_view(),
        name='api-attendance-summary',
    ),
    path('api/v1/grade-summary/', GradeSummaryAPIView.as_view(), name='api-grade-summary'),
]

urlpatterns += router.urls

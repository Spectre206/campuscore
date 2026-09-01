# academics/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import (
    DepartmentViewSet,
    ProgramViewSet,
    CourseViewSet,
    SectionViewSet,
    EnrollmentViewSet,
    AttendanceSessionViewSet,
    AttendanceRecordViewSet,
    AttendanceSummaryAPIView,
    AssessmentViewSet,
    GradeViewSet,
    GradeSummaryAPIView,
)

router = DefaultRouter()
router.register(r'api/v1/departments', DepartmentViewSet, basename='department')
router.register(r'api/v1/programs', ProgramViewSet, basename='program')
router.register(r'api/v1/courses', CourseViewSet, basename='course')
router.register(r'api/v1/sections', SectionViewSet, basename='section')
router.register(r'api/v1/enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'api/v1/attendance-sessions', AttendanceSessionViewSet, basename='attendance-session')
router.register(r'api/v1/attendance-records', AttendanceRecordViewSet, basename='attendance-record')
router.register(r'api/v1/assessments', AssessmentViewSet, basename='assessment')
router.register(r'api/v1/grades', GradeViewSet, basename='grade')

urlpatterns = [
    # Web views
    path('departments/', views.department_list, name='department-list'),
    path('my-sections/', views.teacher_section_list, name='teacher-section-list'),
    path('my-enrollments/', views.student_enrollment_list, name='student-enrollment-list'),

    # Custom API endpoints (non-ViewSet)
    path('api/v1/attendance-summary/', AttendanceSummaryAPIView.as_view(), name='api-attendance-summary'),
    path('api/v1/grade-summary/', GradeSummaryAPIView.as_view(), name='api-grade-summary'),
]

urlpatterns += router.urls
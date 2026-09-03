from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from academics.models import (
    Assessment,
    AttendanceRecord,
    AttendanceSession,
    Course,
    Department,
    Enrollment,
    Grade,
    Program,
    Section,
)
from notifications.models import Notification

from .decorators import role_required
from .models import User


@login_required
def home(request):
    if request.user.role == User.Role.ADMIN:
        return redirect('admin-dashboard')
    elif request.user.role == User.Role.TEACHER:
        return redirect('teacher-dashboard')
    else:
        return redirect('student-dashboard')


@login_required
@role_required([User.Role.ADMIN])
def admin_dashboard(request):
    context = {
        'total_departments': Department.objects.count(),
        'total_programs': Program.objects.count(),
        'total_courses': Course.objects.count(),
        'total_sections': Section.objects.count(),
        'total_teachers': User.objects.filter(role=User.Role.TEACHER).count(),
        'total_students': User.objects.filter(role=User.Role.STUDENT).count(),
        'recent_notifications': Notification.objects.filter(recipient=request.user)[:5],
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
@role_required([User.Role.TEACHER])
def teacher_dashboard(request):
    teacher = request.user
    sections = Section.objects.filter(teacher=teacher).select_related('course')
    section_ids = sections.values_list('id', flat=True)
    upcoming_sessions = AttendanceSession.objects.filter(
        section__in=section_ids, date__gte=timezone.now().date()
    ).order_by('date')[:5]
    recent_assessments = Assessment.objects.filter(section__in=section_ids).order_by('-date')[:5]
    context = {
        'sections_count': sections.count(),
        'sections': sections,
        'upcoming_sessions': upcoming_sessions,
        'recent_assessments': recent_assessments,
    }
    return render(request, 'accounts/teacher_dashboard.html', context)


@login_required
@role_required([User.Role.STUDENT])
def student_dashboard(request):
    student = request.user
    enrollments = Enrollment.objects.filter(
        student=student, status=Enrollment.Status.ACTIVE
    ).select_related('section__course')
    enrollment_ids = enrollments.values_list('id', flat=True)

    # Attendance summary
    total_attendance = AttendanceRecord.objects.filter(enrollment__in=enrollment_ids).count()
    present_count = AttendanceRecord.objects.filter(
        enrollment__in=enrollment_ids, status=AttendanceRecord.Status.PRESENT
    ).count()
    attendance_percentage = (present_count / total_attendance * 100) if total_attendance else 0

    # Recent grades
    recent_grades = (
        Grade.objects.filter(enrollment__in=enrollment_ids)
        .select_related('assessment')
        .order_by('-assessment__date')[:5]
    )

    context = {
        'enrollments': enrollments,
        'attendance_percentage': round(attendance_percentage, 2),
        'recent_grades': recent_grades,
    }
    return render(request, 'accounts/student_dashboard.html', context)

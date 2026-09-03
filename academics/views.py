from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

from accounts.decorators import role_required
from accounts.models import User

from .forms import AttendanceSessionForm
from .models import AttendanceRecord, AttendanceSession, Department, Enrollment, Section


@login_required
def department_list(request):
    query = request.GET.get('q', '')
    departments = Department.objects.all()
    if query:
        departments = departments.filter(Q(name__icontains=query) | Q(code__icontains=query))

    paginator = Paginator(departments, 5)  # 5 departments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'departments': page_obj,
        'query': query,
    }

    # If HTMX request, return only the table partial
    if request.headers.get('HX-Request') == 'true':
        html = render_to_string(
            'academics/partials/department_table.html', context, request=request
        )
        return HttpResponse(html)

    return render(request, 'academics/department_list.html', context)


@login_required
@role_required([User.Role.TEACHER])
def teacher_section_list(request):
    query = request.GET.get('q', '')
    sections = Section.objects.filter(teacher=request.user).select_related('course')
    if query:
        sections = sections.filter(
            Q(name__icontains=query)
            | Q(course__name__icontains=query)
            | Q(course__code__icontains=query)
        )
    paginator = Paginator(sections, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {'sections': page_obj, 'query': query}
    if request.headers.get('HX-Request') == 'true':
        html = render_to_string('academics/partials/section_table.html', context, request=request)
        return HttpResponse(html)
    return render(request, 'academics/teacher_section_list.html', context)


@login_required
@role_required([User.Role.STUDENT])
def student_enrollment_list(request):
    query = request.GET.get('q', '')
    enrollments = Enrollment.objects.filter(student=request.user).select_related('section__course')
    if query:
        enrollments = enrollments.filter(
            Q(section__name__icontains=query)
            | Q(section__course__name__icontains=query)
            | Q(section__course__code__icontains=query)
        )
    paginator = Paginator(enrollments, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {'enrollments': page_obj, 'query': query}
    if request.headers.get('HX-Request') == 'true':
        html = render_to_string(
            'academics/partials/enrollment_table.html', context, request=request
        )
        return HttpResponse(html)
    return render(request, 'academics/student_enrollment_list.html', context)


@login_required
@role_required([User.Role.TEACHER])
def section_attendance_sessions(request, section_id):
    section = get_object_or_404(Section, pk=section_id, teacher=request.user)
    sessions = AttendanceSession.objects.filter(section=section).order_by('-date')
    return render(
        request,
        'academics/attendance_session_list.html',
        {
            'section': section,
            'sessions': sessions,
        },
    )


@login_required
@role_required([User.Role.TEACHER])
def attendance_session_create(request, section_id):
    section = get_object_or_404(Section, pk=section_id, teacher=request.user)
    if request.method == 'POST':
        form = AttendanceSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.section = section
            session.created_by = request.user
            session.save()
            return redirect('section-attendance-session-list', section_id=section.id)
    else:
        form = AttendanceSessionForm()
    return render(
        request,
        'academics/attendance_session_form.html',
        {
            'form': form,
            'section': section,
        },
    )


@login_required
@role_required([User.Role.TEACHER])
def attendance_mark(request, session_id):
    session = get_object_or_404(AttendanceSession, pk=session_id, section__teacher=request.user)
    section = session.section
    enrollments = Enrollment.objects.filter(
        section=section, status=Enrollment.Status.ACTIVE
    ).order_by('student__username')

    AttendanceRecordFormSet = modelformset_factory(
        AttendanceRecord,
        fields=['status', 'remarks'],
        extra=0,
    )

    if request.method == 'POST':
        formset = AttendanceRecordFormSet(request.POST)
        if formset.is_valid():
            for form, enrollment in zip(formset, enrollments):
                status = form.cleaned_data.get('status')
                remarks = form.cleaned_data.get('remarks', '')
                AttendanceRecord.objects.update_or_create(
                    session=session,
                    enrollment=enrollment,
                    defaults={'status': status, 'remarks': remarks},
                )
            return redirect('section-attendance-session-list', section_id=section.id)
    else:
        initial_data = []
        existing_records = {
            r.enrollment_id: r for r in AttendanceRecord.objects.filter(session=session)
        }
        for enrollment in enrollments:
            record = existing_records.get(enrollment.id)
            initial_data.append(
                {
                    'status': record.status if record else AttendanceRecord.Status.PRESENT,
                    'remarks': record.remarks if record else '',
                }
            )
        formset = AttendanceRecordFormSet(
            queryset=AttendanceRecord.objects.none(),
            initial=initial_data,
        )

    form_enrollment_pairs = zip(formset, enrollments)
    context = {
        'session': session,
        'section': section,
        'form_enrollment_pairs': form_enrollment_pairs,
        'formset': formset,
    }
    return render(request, 'academics/attendance_mark.html', context)


@login_required
@role_required([User.Role.STUDENT])
def student_attendance_summary(request):
    enrollments = Enrollment.objects.filter(student=request.user, status=Enrollment.Status.ACTIVE)
    summary = []
    for enrollment in enrollments:
        section = enrollment.section
        sessions = AttendanceSession.objects.filter(section=section)
        total_sessions = sessions.count()
        present_count = AttendanceRecord.objects.filter(
            enrollment=enrollment, status=AttendanceRecord.Status.PRESENT
        ).count()
        percentage = (present_count / total_sessions * 100) if total_sessions else 0
        summary.append(
            {
                'section': section,
                'course_code': section.course.code,
                'total_sessions': total_sessions,
                'present': present_count,
                'percentage': round(percentage, 2),
            }
        )
    return render(request, 'academics/student_attendance_summary.html', {'summary': summary})

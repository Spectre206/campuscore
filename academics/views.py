from django.shortcuts import render
from .models import Department, Section, Enrollment
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from accounts.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import render_to_string
@login_required
def department_list(request):
    query = request.GET.get('q', '')
    departments = Department.objects.all()
    if query:
        departments = departments.filter(
            Q(name__icontains=query) | Q(code__icontains=query)
        )

    paginator = Paginator(departments, 5)  # 5 departments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'departments': page_obj,
        'query': query,
    }

    # If HTMX request, return only the table partial
    if request.headers.get('HX-Request') == 'true':
        html = render_to_string('academics/partials/department_table.html', context, request=request)
        return HttpResponse(html)

    return render(request, 'academics/department_list.html', context)
@login_required
@role_required([User.Role.TEACHER])
def teacher_section_list(request):
    query = request.GET.get('q', '')
    sections = Section.objects.filter(teacher=request.user).select_related('course')
    if query:
        sections = sections.filter(
            Q(name__icontains=query) |
            Q(course__name__icontains=query) |
            Q(course__code__icontains=query)
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
            Q(section__name__icontains=query) |
            Q(section__course__name__icontains=query) |
            Q(section__course__code__icontains=query)
        )
    paginator = Paginator(enrollments, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {'enrollments': page_obj, 'query': query}
    if request.headers.get('HX-Request') == 'true':
        html = render_to_string('academics/partials/enrollment_table.html', context, request=request)
        return HttpResponse(html)
    return render(request, 'academics/student_enrollment_list.html', context)

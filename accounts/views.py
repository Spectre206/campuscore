from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

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


@role_required([User.Role.ADMIN])
def admin_dashboard(request):
    return render(request, 'accounts/admin_dashboard.html')


@role_required([User.Role.TEACHER])
def teacher_dashboard(request):
    return render(request, 'accounts/teacher_dashboard.html')


@role_required([User.Role.STUDENT])
def student_dashboard(request):
    return render(request, 'accounts/student_dashboard.html')

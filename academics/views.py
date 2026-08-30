from django.shortcuts import render
from .models import Department
from django.contrib.auth.decorators import login_required

@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'academics/department_list.html', {'departments': departments})
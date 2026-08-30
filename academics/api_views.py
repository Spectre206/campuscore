from rest_framework.generics import ListCreateAPIView
from .models import Department, Program, Course
from .serializers import DepartmentSerializer, ProgramSerializer, CourseSerializer

class DepartmentListCreateAPIView(ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class ProgramListCreateAPIView(ListCreateAPIView):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer


class CourseListCreateAPIView(ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
from rest_framework.generics import ListCreateAPIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from .models import Department, Program, Course
from .serializers import DepartmentSerializer, ProgramSerializer, CourseSerializer
from .permissions import IsAdminOrReadOnly

class DepartmentListCreateAPIView(ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]  # optional; DRF default includes these
    permission_classes = [IsAdminOrReadOnly]

class ProgramListCreateAPIView(ListCreateAPIView):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [IsAdminOrReadOnly]

class CourseListCreateAPIView(ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]
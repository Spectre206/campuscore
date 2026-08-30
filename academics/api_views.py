from django.db import transaction
from rest_framework.generics import ListCreateAPIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.exceptions import ValidationError
from .models import Department, Program, Course, Section, Enrollment
from .serializers import DepartmentSerializer, ProgramSerializer, CourseSerializer, SectionSerializer, EnrollmentSerializer
from .permissions import IsAdminOrReadOnly, IsAdminOrTeacher

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

class SectionListCreateAPIView(ListCreateAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAdminOrTeacher]

class EnrollmentListCreateAPIView(ListCreateAPIView):
    serializer_class = EnrollmentSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        user = self.request.user
        if user.role == user.Role.STUDENT:
            return Enrollment.objects.filter(student=user)
        return Enrollment.objects.all()

    def perform_create(self, serializer):
        section = serializer.validated_data['section']
        student = serializer.validated_data['student']

        # Use transaction with select_for_update to prevent race conditions
        with transaction.atomic():
            # Lock the section row to safely check capacity and duplicates
            locked_section = Section.objects.select_for_update().get(pk=section.pk)

            # Check duplicate enrollment
            if Enrollment.objects.filter(section=locked_section, student=student).exists():
                raise ValidationError({"detail": "Student is already enrolled in this section."})

            # Check capacity (if not None)
            if locked_section.capacity is not None:
                enrolled_count = Enrollment.objects.filter(section=locked_section, status='ACTIVE').count()
                if enrolled_count >= locked_section.capacity:
                    raise ValidationError({"detail": "Section capacity exceeded."})

            serializer.save()
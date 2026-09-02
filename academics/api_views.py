# academics/api_views.py
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from accounts.models import User

from .models import (
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
from .permissions import IsAdminOrReadOnly, IsAdminOrTeacher
from .serializers import (
    AssessmentSerializer,
    AttendanceRecordSerializer,
    AttendanceSessionSerializer,
    AttendanceSummarySerializer,
    CourseSerializer,
    DepartmentSerializer,
    EnrollmentSerializer,
    GradeSerializer,
    GradeSummarySerializer,
    ProgramSerializer,
    SectionSerializer,
)


class DepartmentViewSet(ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'id']


class ProgramViewSet(ModelViewSet):
    queryset = Program.objects.select_related('department').all()
    serializer_class = ProgramSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['name', 'code', 'department']
    ordering_fields = ['name', 'code', 'id']


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.select_related('program').all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['name', 'code', 'program']
    ordering_fields = ['name', 'code', 'id']


class SectionViewSet(ModelViewSet):
    queryset = Section.objects.select_related('course', 'teacher').all()
    serializer_class = SectionSerializer
    permission_classes = [IsAdminOrTeacher]
    filterset_fields = ['name', 'course', 'teacher', 'is_active']
    ordering_fields = ['name', 'id']


class EnrollmentViewSet(ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAdminOrTeacher]
    filterset_fields = ['section', 'student', 'status']
    ordering_fields = ['enrolled_at', 'id']

    def get_queryset(self):
        user = self.request.user
        queryset = Enrollment.objects.select_related('section', 'student')
        if user.role == user.Role.STUDENT:
            queryset = queryset.filter(student=user)
        return queryset

    def perform_create(self, serializer):
        section = serializer.validated_data['section']
        student = serializer.validated_data['student']

        with transaction.atomic():
            locked_section = Section.objects.select_for_update().get(pk=section.pk)
            if Enrollment.objects.filter(section=locked_section, student=student).exists():
                raise ValidationError({'detail': 'Student is already enrolled in this section.'})
            if locked_section.capacity is not None:
                enrolled_count = Enrollment.objects.filter(
                    section=locked_section, status='ACTIVE'
                ).count()
                if enrolled_count >= locked_section.capacity:
                    raise ValidationError({'detail': 'Section capacity exceeded.'})
            serializer.save()


class AttendanceSessionViewSet(ModelViewSet):
    serializer_class = AttendanceSessionSerializer
    permission_classes = [IsAdminOrTeacher]
    filterset_fields = ['section', 'date', 'created_by']
    ordering_fields = ['date', 'id']

    def get_queryset(self):
        user = self.request.user
        queryset = AttendanceSession.objects.select_related('section', 'created_by')
        if user.role == user.Role.TEACHER:
            queryset = queryset.filter(section__teacher=user)
        return queryset


class AttendanceRecordViewSet(ModelViewSet):
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAdminOrTeacher]
    filterset_fields = ['session', 'enrollment', 'status']
    ordering_fields = ['id']

    def get_queryset(self):
        user = self.request.user
        queryset = AttendanceRecord.objects.select_related(
            'session__section', 'enrollment__student'
        )
        if user.role == user.Role.TEACHER:
            queryset = queryset.filter(session__section__teacher=user)
        return queryset

    def create(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        with transaction.atomic():
            serializer.save()


class AssessmentViewSet(ModelViewSet):
    serializer_class = AssessmentSerializer
    permission_classes = [IsAdminOrTeacher]
    filterset_fields = ['section', 'type', 'date']
    ordering_fields = ['date', 'name', 'id']

    def get_queryset(self):
        user = self.request.user
        queryset = Assessment.objects.select_related('section')
        if user.role == user.Role.TEACHER:
            queryset = queryset.filter(section__teacher=user)
        return queryset


class GradeViewSet(ModelViewSet):
    serializer_class = GradeSerializer
    permission_classes = [IsAdminOrTeacher]
    filterset_fields = ['assessment', 'enrollment', 'marks']
    ordering_fields = ['marks', 'id']

    def get_queryset(self):
        user = self.request.user
        queryset = Grade.objects.select_related('assessment', 'enrollment__student')
        if user.role == user.Role.TEACHER:
            queryset = queryset.filter(assessment__section__teacher=user)
        return queryset

    def create(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        with transaction.atomic():
            serializer.save()


class AttendanceSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: AttendanceSummarySerializer(many=True)})
    def get(self, request):
        user = request.user
        student_id = request.query_params.get('student_id')

        if user.role == user.Role.STUDENT:
            if student_id and str(student_id) != str(user.id):
                return Response(
                    {'detail': "You cannot view another student's summary."}, status=403
                )
            student_id = user.id
        elif user.role in [user.Role.ADMIN, user.Role.TEACHER]:
            if not student_id:
                return Response(
                    {'detail': 'student_id query parameter required for admin/teacher.'}, status=400
                )
        else:
            return Response({'detail': 'Invalid role.'}, status=403)

        student = get_object_or_404(User, pk=student_id, role=User.Role.STUDENT)
        enrollments = Enrollment.objects.filter(student=student)
        summary = []
        for enrollment in enrollments:
            sessions = AttendanceSession.objects.filter(section=enrollment.section)
            total_sessions = sessions.count()
            present_count = AttendanceRecord.objects.filter(
                enrollment=enrollment, status=AttendanceRecord.Status.PRESENT
            ).count()
            attendance_percentage = (present_count / total_sessions * 100) if total_sessions else 0
            summary.append(
                {
                    'section': enrollment.section.name,
                    'course_code': enrollment.section.course.code,
                    'total_sessions': total_sessions,
                    'present': present_count,
                    'percentage': round(attendance_percentage, 2),
                }
            )
        return Response(summary)


class GradeSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: GradeSummarySerializer(many=True)})
    def get(self, request):
        user = request.user
        student_id = request.query_params.get('student_id')

        if user.role == user.Role.STUDENT:
            if student_id and str(student_id) != str(user.id):
                return Response({'detail': "You cannot view another student's grades."}, status=403)
            student_id = user.id
        elif user.role in [user.Role.ADMIN, user.Role.TEACHER]:
            if not student_id:
                return Response(
                    {'detail': 'student_id query parameter required for admin/teacher.'}, status=400
                )
        else:
            return Response({'detail': 'Invalid role.'}, status=403)

        student = get_object_or_404(User, pk=student_id, role=User.Role.STUDENT)
        enrollments = Enrollment.objects.filter(student=student)
        summary = []
        for enrollment in enrollments:
            grades = Grade.objects.filter(enrollment=enrollment)
            total_marks_obtained = sum(g.marks for g in grades)
            total_possible = sum(g.assessment.total_marks for g in grades)
            percentage = (total_marks_obtained / total_possible * 100) if total_possible else 0
            summary.append(
                {
                    'section': enrollment.section.name,
                    'course_code': enrollment.section.course.code,
                    'assessments_count': grades.count(),
                    'total_marks_obtained': total_marks_obtained,
                    'total_possible_marks': total_possible,
                    'percentage': round(percentage, 2),
                }
            )
        return Response(summary)

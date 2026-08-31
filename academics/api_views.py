# academics/api_views.py
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from accounts.models import User
from .models import (
    Department, Program, Course, Section, Enrollment,
    AttendanceSession, AttendanceRecord, Assessment, Grade
)
from .serializers import (
    DepartmentSerializer, ProgramSerializer, CourseSerializer,
    SectionSerializer, EnrollmentSerializer,
    AttendanceSessionSerializer, AttendanceRecordSerializer,
    AssessmentSerializer, GradeSerializer
)
from .permissions import IsAdminOrReadOnly, IsAdminOrTeacher


class DepartmentListCreateAPIView(ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAdminOrReadOnly]


class ProgramListCreateAPIView(ListCreateAPIView):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAdminOrReadOnly]


class CourseListCreateAPIView(ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
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

        with transaction.atomic():
            locked_section = Section.objects.select_for_update().get(pk=section.pk)
            if Enrollment.objects.filter(section=locked_section, student=student).exists():
                raise ValidationError({"detail": "Student is already enrolled in this section."})
            if locked_section.capacity is not None:
                enrolled_count = Enrollment.objects.filter(section=locked_section, status='ACTIVE').count()
                if enrolled_count >= locked_section.capacity:
                    raise ValidationError({"detail": "Section capacity exceeded."})
            serializer.save()


class AttendanceSessionListCreateAPIView(ListCreateAPIView):
    queryset = AttendanceSession.objects.all()
    serializer_class = AttendanceSessionSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        user = self.request.user
        if user.role == user.Role.TEACHER:
            return AttendanceSession.objects.filter(section__teacher=user)
        return AttendanceSession.objects.all()


class AttendanceRecordListCreateAPIView(ListCreateAPIView):
    serializer_class = AttendanceRecordSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        user = self.request.user
        if user.role == user.Role.TEACHER:
            return AttendanceRecord.objects.filter(session__section__teacher=user)
        return AttendanceRecord.objects.all()

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

    def get(self, request):
        user = request.user
        student_id = request.query_params.get('student_id')

        if user.role == user.Role.STUDENT:
            if student_id and str(student_id) != str(user.id):
                return Response({"detail": "You cannot view another student's summary."}, status=403)
            student_id = user.id
        elif user.role in [user.Role.ADMIN, user.Role.TEACHER]:
            if not student_id:
                return Response({"detail": "student_id query parameter required for admin/teacher."}, status=400)
        else:
            return Response({"detail": "Invalid role."}, status=403)

        student = get_object_or_404(User, pk=student_id, role=User.Role.STUDENT)
        enrollments = Enrollment.objects.filter(student=student)
        summary = []
        for enrollment in enrollments:
            sessions = AttendanceSession.objects.filter(section=enrollment.section)
            total_sessions = sessions.count()
            present_count = AttendanceRecord.objects.filter(
                enrollment=enrollment,
                status=AttendanceRecord.Status.PRESENT
            ).count()
            attendance_percentage = (present_count / total_sessions * 100) if total_sessions else 0
            summary.append({
                'section': enrollment.section.name,
                'course_code': enrollment.section.course.code,
                'total_sessions': total_sessions,
                'present': present_count,
                'percentage': round(attendance_percentage, 2)
            })
        return Response(summary)

class AssessmentListCreateAPIView(ListCreateAPIView):
    serializer_class = AssessmentSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        user = self.request.user
        if user.role == user.Role.TEACHER:
            return Assessment.objects.filter(section__teacher=user)
        return Assessment.objects.all()


class GradeListCreateAPIView(ListCreateAPIView):
    serializer_class = GradeSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        user = self.request.user
        if user.role == user.Role.TEACHER:
            return Grade.objects.filter(assessment__section__teacher=user)
        return Grade.objects.all()

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


class GradeSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        student_id = request.query_params.get('student_id')

        if user.role == user.Role.STUDENT:
            if student_id and str(student_id) != str(user.id):
                return Response({"detail": "You cannot view another student's grades."}, status=403)
            student_id = user.id
        elif user.role in [user.Role.ADMIN, user.Role.TEACHER]:
            if not student_id:
                return Response({"detail": "student_id query parameter required for admin/teacher."}, status=400)
        else:
            return Response({"detail": "Invalid role."}, status=403)

        student = get_object_or_404(User, pk=student_id, role=User.Role.STUDENT)
        enrollments = Enrollment.objects.filter(student=student)
        summary = []
        for enrollment in enrollments:
            grades = Grade.objects.filter(enrollment=enrollment)
            total_marks_obtained = sum(g.marks for g in grades)
            total_possible = sum(g.assessment.total_marks for g in grades)
            percentage = (total_marks_obtained / total_possible * 100) if total_possible else 0
            summary.append({
                'section': enrollment.section.name,
                'course_code': enrollment.section.course.code,
                'assessments_count': grades.count(),
                'total_marks_obtained': total_marks_obtained,
                'total_possible_marks': total_possible,
                'percentage': round(percentage, 2)
            })
        return Response(summary)
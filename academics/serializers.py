from rest_framework import serializers
from .models import Department, Program, Course, Section, Enrollment, AttendanceSession, AttendanceRecord, Assessment, Grade

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code']
        
class ProgramSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Program
        fields = ['id', 'name', 'code', 'department', 'department_name']


class CourseSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source='program.name', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'description', 'program', 'program_name']
        
class SectionSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    teacher_username = serializers.CharField(source='teacher.username', read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'name', 'capacity', 'is_active', 'course', 'course_name', 'teacher', 'teacher_username']

    def validate_teacher(self, value):
        if value.role != 'TEACHER':
            raise serializers.ValidationError("Assigned user must have role 'TEACHER'.")
        return value


class EnrollmentSerializer(serializers.ModelSerializer):
    section_name = serializers.CharField(source='section.name', read_only=True)
    student_username = serializers.CharField(source='student.username', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'section', 'section_name', 'student', 'student_username', 'status', 'enrolled_at']
        read_only_fields = ['enrolled_at']

    def validate_student(self, value):
        if value.role != 'STUDENT':
            raise serializers.ValidationError("Enrolled user must have role 'STUDENT'.")
        return value

class AttendanceSessionSerializer(serializers.ModelSerializer):
    section_name = serializers.CharField(source='section.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = AttendanceSession
        fields = ['id', 'section', 'section_name', 'date', 'title', 'created_by', 'created_by_username']

    def validate_section(self, value):
        request = self.context.get('request')
        if request and request.user.role == request.user.Role.TEACHER:
            # Teacher can only create sessions for sections they teach
            if not Section.objects.filter(pk=value.pk, teacher=request.user).exists():
                raise serializers.ValidationError("You can only create sessions for your own sections.")
        return value


class AttendanceRecordSerializer(serializers.ModelSerializer):
    session_section = serializers.CharField(source='session.section.name', read_only=True)
    student_username = serializers.CharField(source='enrollment.student.username', read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = ['id', 'session', 'session_section', 'enrollment', 'student_username', 'status', 'remarks']

    def validate(self, data):
        session = data.get('session')
        enrollment = data.get('enrollment')
        if session and enrollment:
            if enrollment.section_id != session.section_id:
                raise serializers.ValidationError("Enrollment does not belong to the session's section.")
        return data

class AssessmentSerializer(serializers.ModelSerializer):
    section_name = serializers.CharField(source='section.name', read_only=True)
    total_marks = serializers.IntegerField(min_value=1)

    class Meta:
        model = Assessment
        fields = ['id', 'name', 'type', 'total_marks', 'date', 'section', 'section_name']

    def validate_section(self, value):
        request = self.context.get('request')
        if request and request.user.role == request.user.Role.TEACHER:
            if not Section.objects.filter(pk=value.pk, teacher=request.user).exists():
                raise serializers.ValidationError("You can only create assessments for your own sections.")
        return value


class GradeSerializer(serializers.ModelSerializer):
    assessment_name = serializers.CharField(source='assessment.name', read_only=True)
    student_username = serializers.CharField(source='enrollment.student.username', read_only=True)

    class Meta:
        model = Grade
        fields = ['id', 'assessment', 'assessment_name', 'enrollment', 'student_username', 'marks', 'remarks']

    def validate(self, data):
        assessment = data.get('assessment')
        enrollment = data.get('enrollment')
        marks = data.get('marks')

        if assessment and enrollment:
            if enrollment.section_id != assessment.section_id:
                raise serializers.ValidationError("Enrollment does not belong to the assessment's section.")
        if assessment and marks is not None:
            if marks < 0 or marks > assessment.total_marks:
                raise serializers.ValidationError({"marks": "Marks must be between 0 and total marks."})
        return data
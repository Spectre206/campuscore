from rest_framework import serializers
from .models import Department, Program, Course, Section, Enrollment

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
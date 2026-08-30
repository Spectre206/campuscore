from rest_framework import serializers
from .models import Department, Program, Course

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
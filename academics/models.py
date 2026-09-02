from django.db import models
from django.conf import settings
from django.db.models import CheckConstraint, Q
from django.core.exceptions import ValidationError

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        ordering = ['id']
       
    def __str__(self):
        return self.name

class Program(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='programs'
    )
    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, default='')
    program = models.ForeignKey(
        Program,
        on_delete=models.PROTECT,
        related_name='courses'
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name

class Section(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name='sections'
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='sections_taught',
        limit_choices_to={'role': 'TEACHER'}  # only for admin form
    )
    name = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['id']
        unique_together = [('course', 'name')]
    def __str__(self):
        return f"{self.course.code} - {self.name}"


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        DROPPED = 'DROPPED', 'Dropped'
        COMPLETED = 'COMPLETED', 'Completed'

    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        related_name='enrollments'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='enrollments',
        limit_choices_to={'role': 'STUDENT'}
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    enrolled_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['id']
        unique_together = [('section', 'student')]

    def __str__(self):
        return f"{self.student.username} in {self.section}"

class AttendanceSession(models.Model):
    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        related_name='attendance_sessions'
    )
    date = models.DateField()
    title = models.CharField(max_length=100, blank=True, default='')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='attendance_sessions_created',
        limit_choices_to={'role': 'TEACHER'}
    )

    class Meta:
        ordering = ['-date']  # latest first

    def __str__(self):
        return f"{self.section} - {self.date}"


class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'PRESENT', 'Present'
        ABSENT = 'ABSENT', 'Absent'
        LATE = 'LATE', 'Late'
        EXCUSED = 'EXCUSED', 'Excused'

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name='records'
    )
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PRESENT, db_index=True)
    remarks = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['id']
        unique_together = [('session', 'enrollment')]
    def __str__(self):
        return f"{self.enrollment.student.username} - {self.status}"

class Assessment(models.Model):
    class Type(models.TextChoices):
        EXAM = 'EXAM', 'Exam'
        QUIZ = 'QUIZ', 'Quiz'
        ASSIGNMENT = 'ASSIGNMENT', 'Assignment'
        PROJECT = 'PROJECT', 'Project'

    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        related_name='assessments'
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=Type.choices)
    total_marks = models.PositiveIntegerField()
    date = models.DateField(db_index=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.name} ({self.section})"


class Grade(models.Model):
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='grades'
    )
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='grades'
    )
    marks = models.IntegerField(db_index=True)
    remarks = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['id']
        unique_together = [('assessment', 'enrollment')]
        constraints = [
            CheckConstraint(condition=Q(marks__gte=0), name='grade_marks_non_negative')
        ]

    def clean(self):
        if self.marks > self.assessment.total_marks:
            raise ValidationError({'marks': 'Marks cannot exceed total marks.'})

    def __str__(self):
        return f"{self.enrollment.student.username} - {self.assessment.name}: {self.marks}"
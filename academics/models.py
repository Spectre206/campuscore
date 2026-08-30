from django.db import models
from django.conf import settings

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

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
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('section', 'student')]

    def __str__(self):
        return f"{self.student.username} in {self.section}"
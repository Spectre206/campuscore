# academics/signals.py

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from notifications.services import notify_user
from notifications.tasks import send_email_task

from .models import Enrollment, Grade


@receiver(post_save, sender=Enrollment)
def enrollment_created_notification(sender, instance, created, **kwargs):
    if created:
        student = instance.student
        section = instance.section
        # In-app notification
        notify_user(
            recipient=student,
            title='Enrollment Successful',
            message=f'You have been enrolled in {section.course.name} - {section.name}.',
            link=reverse('student-enrollment-list'),
        )
        # Async email notification
        if student.email:
            subject = 'Enrollment Successful'
            message = (
                f'Dear {student.get_full_name() or student.username},\n\n'
                f'You have been enrolled in {section.course.name} - {section.name}.\n\n'
                'CampusCore'
            )
            transaction.on_commit(lambda: send_email_task.delay(subject, message, [student.email]))


@receiver(post_save, sender=Grade)
def grade_created_notification(sender, instance, created, **kwargs):
    if created:
        student = instance.enrollment.student
        assessment = instance.assessment
        # In-app notification
        notify_user(
            recipient=student,
            title='Grade Posted',
            message=(
                f'Your grade for {assessment.name} is {instance.marks}/{assessment.total_marks}.'
            ),
            link=reverse('student-enrollment-list'),
        )
        # Async email notification
        if student.email:
            subject = 'Grade Posted'
            message = (
                f'Dear {student.get_full_name() or student.username},\n\n'
                f'Your grade for {assessment.name} is '
                f'{instance.marks}/{assessment.total_marks}.\n\n'
                'CampusCore'
            )
            transaction.on_commit(lambda: send_email_task.delay(subject, message, [student.email]))

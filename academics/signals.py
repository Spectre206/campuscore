from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from .models import Enrollment, Grade
from notifications.services import notify_user

@receiver(post_save, sender=Enrollment)
def enrollment_created_notification(sender, instance, created, **kwargs):
    if created:
        student = instance.student
        section = instance.section
        notify_user(
            recipient=student,
            title="Enrollment Successful",
            message=f"You have been enrolled in {section.course.name} - {section.name}.",
            link=reverse('student-enrollment-list')
        )

@receiver(post_save, sender=Grade)
def grade_created_notification(sender, instance, created, **kwargs):
    if created:
        student = instance.enrollment.student
        assessment = instance.assessment
        notify_user(
            recipient=student,
            title="Grade Posted",
            message=f"Your grade for {assessment.name} is {instance.marks}/{assessment.total_marks}.",
            link=reverse('student-enrollment-list')  # or later a dedicated grades page
        )
from django.conf import settings
from django.db import models
from django.utils import timezone
class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=100)
    message = models.TextField()
    link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"

    @property
    def is_read(self):
        return self.read_at is not None

    def mark_as_read(self):
        if not self.is_read:
            self.read_at = timezone.now()
            self.save(update_fields=['read_at'])
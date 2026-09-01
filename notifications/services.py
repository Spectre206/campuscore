from .models import Notification

def notify_user(recipient, title, message, link=None):
    """
    Create a notification for a user.
    """
    if recipient is None:
        return None
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        link=link
    )
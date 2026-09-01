from .models import Notification

def unread_notifications_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(recipient=request.user, read_at__isnull=True).count()
    else:
        count = 0
    return {'unread_count': count}
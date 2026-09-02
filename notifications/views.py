from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone

from .models import Notification


@login_required
def notification_list(request):
    filter_type = request.GET.get('filter', 'all')
    notifications = Notification.objects.filter(recipient=request.user)

    if filter_type == 'unread':
        notifications = notifications.filter(read_at__isnull=True)
    elif filter_type == 'read':
        notifications = notifications.filter(read_at__isnull=False)

    paginator = Paginator(notifications, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'notifications': page_obj,
        'filter': filter_type,
    }

    if request.headers.get('HX-Request') == 'true':
        html = render_to_string(
            'notifications/partials/notification_items.html', context, request=request
        )
        return HttpResponse(html)

    return render(request, 'notifications/notification_list.html', context)


@login_required
def notification_detail(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    if not notification.is_read:
        notification.mark_as_read()

    if notification.link:
        return redirect(notification.link)
    return redirect('notification-list')


@login_required
def mark_all_read(request):
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user, read_at__isnull=True).update(
            read_at=timezone.now()
        )
        if request.headers.get('HX-Request') == 'true':
            # Return updated list and badge
            notifications = Notification.objects.filter(recipient=request.user)[:10]
            context = {'notifications': notifications, 'filter': 'all'}
            html = render_to_string(
                'notifications/partials/notification_items.html', context, request=request
            )
            badge_html = render_to_string(
                'notifications/partials/unread_badge.html', {'unread_count': 0}, request=request
            )
            return HttpResponse(
                html + badge_html
            )  # Could be separate targets; we'll handle differently later
        return redirect('notification-list')
    return redirect('notification-list')


@login_required
def unread_count(request):
    count = Notification.objects.filter(recipient=request.user, read_at__isnull=True).count()
    html = render_to_string(
        'notifications/partials/unread_badge.html', {'unread_count': count}, request=request
    )
    return HttpResponse(html)
